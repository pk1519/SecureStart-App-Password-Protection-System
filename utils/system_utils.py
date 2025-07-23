"""
System utilities for AppLock
Includes admin checks, password prompts, and system integration
"""

import sys
import os
import ctypes
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog
import winreg
from pathlib import Path
from typing import List, Dict, Optional
import threading
import time

def is_admin() -> bool:
    """Check if the current process is running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart the application as administrator"""
    if is_admin():
        return
    
    try:
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            " ".join(sys.argv), 
            None, 
            1
        )
    except Exception as e:
        print(f"Failed to restart as admin: {e}")

class PasswordDialog:
    """Custom password dialog with timeout support"""
    
    def __init__(self, app_name: str, timeout: int = 15):
        self.app_name = app_name
        self.timeout = timeout
        self.result = None
        self.dialog_closed = False
        
    def show(self) -> Optional[str]:
        """Show the password dialog and return the password or None"""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Create custom dialog
        dialog = tk.Toplevel(root)
        dialog.title("AppLock - Authentication Required")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Always on top and centered
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        tk.Label(dialog, text=f"🔒 {self.app_name} is protected", 
                font=("Arial", 14, "bold")).pack(pady=20)
        
        tk.Label(dialog, text="Enter password to continue:", 
                font=("Arial", 10)).pack(pady=5)
        
        # Password entry
        password_var = tk.StringVar()
        password_entry = tk.Entry(dialog, textvariable=password_var, 
                                show="*", font=("Arial", 12), width=30)
        password_entry.pack(pady=10)
        password_entry.focus()
        
        # Timeout label
        timeout_var = tk.StringVar()
        timeout_var.set(f"Timeout in {self.timeout} seconds")
        timeout_label = tk.Label(dialog, textvariable=timeout_var, 
                               font=("Arial", 9), fg="red")
        timeout_label.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def on_ok():
            self.result = password_var.get()
            self.dialog_closed = True
            dialog.destroy()
            root.destroy()
        
        def on_cancel():
            self.result = None
            self.dialog_closed = True
            dialog.destroy()
            root.destroy()
        
        tk.Button(button_frame, text="OK", command=on_ok, 
                 font=("Arial", 10), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=on_cancel, 
                 font=("Arial", 10), width=10).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        password_entry.bind('<Return>', lambda e: on_ok())
        
        # Timeout handler
        def countdown():
            remaining = self.timeout
            while remaining > 0 and not self.dialog_closed:
                timeout_var.set(f"Timeout in {remaining} seconds")
                time.sleep(1)
                remaining -= 1
            
            if not self.dialog_closed:
                self.result = None
                self.dialog_closed = True
                try:
                    dialog.destroy()
                    root.destroy()
                except:
                    pass
        
        # Start countdown in separate thread
        countdown_thread = threading.Thread(target=countdown, daemon=True)
        countdown_thread.start()
        
        try:
            root.mainloop()
        except:
            pass
        
        return self.result

def prompt_for_password(app_name: str, timeout: int = 15) -> bool:
    """Prompt user for password and verify it"""
    from core.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    
    if not config_manager.has_password():
        messagebox.showerror("Error", "No master password set!")
        return False
    
    if not config_manager.get_setting('protection_enabled', True):
        return True  # Protection is disabled
    
    dialog = PasswordDialog(app_name, timeout)
    password = dialog.show()
    
    if password is None:
        return False
    
    return config_manager.verify_password(password)

def get_installed_programs() -> List[Dict[str, str]]:
    """Get list of installed programs from Windows registry"""
    programs = []
    
    # Registry paths to check
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    
    for hkey, reg_path in reg_paths:
        try:
            with winreg.OpenKey(hkey, reg_path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                try:
                                    install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                    if install_location and os.path.exists(install_location):
                                        # Find .exe files in install location
                                        for file_path in Path(install_location).rglob("*.exe"):
                                            if file_path.is_file():
                                                programs.append({
                                                    'name': name,
                                                    'path': str(file_path),
                                                    'type': 'exe'
                                                })
                                                break  # Only add the first .exe found
                                except FileNotFoundError:
                                    pass
                            except FileNotFoundError:
                                pass
                    except (OSError, FileNotFoundError):
                        continue
        except (OSError, FileNotFoundError):
            continue
    
    # Remove duplicates based on path
    seen_paths = set()
    unique_programs = []
    for program in programs:
        if program['path'] not in seen_paths:
            seen_paths.add(program['path'])
            unique_programs.append(program)
    
    return unique_programs

def get_uwp_apps() -> List[Dict[str, str]]:
    """Get list of UWP/Microsoft Store apps"""
    apps = []
    
    try:
        # Use PowerShell to get UWP apps
        result = subprocess.run([
            'powershell', '-Command',
            'Get-AppxPackage | Where-Object {$_.Name -notlike "*Microsoft.Windows*"} | Select-Object Name, PackageFamilyName, InstallLocation'
        ], capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            current_app = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('Name'):
                    if current_app:
                        apps.append(current_app)
                        current_app = {}
                    current_app['name'] = line.split(':', 1)[1].strip()
                elif line.startswith('PackageFamilyName'):
                    current_app['package_family_name'] = line.split(':', 1)[1].strip()
                elif line.startswith('InstallLocation'):
                    current_app['path'] = line.split(':', 1)[1].strip()
                    current_app['type'] = 'uwp'
            
            if current_app:
                apps.append(current_app)
    
    except Exception as e:
        print(f"Error getting UWP apps: {e}")
    
    return apps

def add_to_startup(enable: bool = True):
    """Add or remove AppLock from Windows startup"""
    app_path = str(Path(sys.argv[0]).absolute())
    startup_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, startup_key, 0, winreg.KEY_SET_VALUE) as key:
            if enable:
                winreg.SetValueEx(key, "AppLock", 0, winreg.REG_SZ, app_path)
            else:
                try:
                    winreg.DeleteValue(key, "AppLock")
                except FileNotFoundError:
                    pass
    except Exception as e:
        print(f"Error modifying startup: {e}")

def is_in_startup() -> bool:
    """Check if AppLock is in Windows startup"""
    startup_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, startup_key) as key:
            try:
                winreg.QueryValueEx(key, "AppLock")
                return True
            except FileNotFoundError:
                return False
    except Exception:
        return False

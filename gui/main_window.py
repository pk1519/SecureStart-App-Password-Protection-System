"""
Main GUI Window for AppLock
Provides interface for managing locked applications and settings
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import Dict, List
import os
from pathlib import Path

from core.config_manager import ConfigManager
from core.app_monitor import AppMonitor
from utils.system_utils import get_installed_programs, get_uwp_apps, add_to_startup, is_in_startup

class AppLockGUI:
    """Main GUI application for AppLock"""
    
    def __init__(self, config_manager: ConfigManager, app_monitor: AppMonitor):
        self.config_manager = config_manager
        self.app_monitor = app_monitor
        
        self.root = tk.Tk()
        self.root.title("AppLock - Application Protection System")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize variables
        self.protection_enabled = tk.BooleanVar(value=self.config_manager.get_setting('protection_enabled', True))
        self.stealth_mode = tk.BooleanVar(value=self.config_manager.get_setting('stealth_mode', False))
        self.log_attempts = tk.BooleanVar(value=self.config_manager.get_setting('log_attempts', True))
        self.startup_with_windows = tk.BooleanVar(value=is_in_startup())
        
        self.create_widgets()
        self.update_locked_apps_list()
        
        # Check if password is set
        if not self.config_manager.has_password():
            self.set_password()
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main tab
        self.create_main_tab(notebook)
        
        # Apps tab
        self.create_apps_tab(notebook)
        
        # Settings tab
        self.create_settings_tab(notebook)
        
        # Logs tab
        self.create_logs_tab(notebook)
    
    def create_main_tab(self, notebook):
        """Create the main control tab"""
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="🏠 Main")
        
        # Title
        title_label = tk.Label(main_frame, text="🛡️ AppLock", 
                              font=("Arial", 20, "bold"), fg="navy")
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(main_frame, text="Desktop Application Protection System", 
                                 font=("Arial", 12), fg="gray")
        subtitle_label.pack(pady=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Protection toggle
        protection_frame = tk.Frame(status_frame)
        protection_frame.pack(fill=tk.X, pady=5)
        
        tk.Checkbutton(protection_frame, text="Enable Protection", 
                      variable=self.protection_enabled, 
                      command=self.toggle_protection,
                      font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        # Status indicators
        self.status_label = tk.Label(status_frame, text="", font=("Arial", 10))
        self.status_label.pack(pady=10)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(main_frame, text="Quick Actions", padding=10)
        actions_frame.pack(fill=tk.X, padx=20, pady=10)
        
        button_frame = tk.Frame(actions_frame)
        button_frame.pack()
        
        tk.Button(button_frame, text="🔑 Change Password", 
                 command=self.change_password, width=15,
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="➕ Add App", 
                 command=self.add_app_dialog, width=15,
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="📊 View Logs", 
                 command=lambda: notebook.select(3), width=15,
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        self.update_status()
    
    def create_apps_tab(self, notebook):
        """Create the applications management tab"""
        apps_frame = ttk.Frame(notebook)
        notebook.add(apps_frame, text="🔒 Protected Apps")
        
        # Toolbar
        toolbar = tk.Frame(apps_frame)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(toolbar, text="➕ Add App", command=self.add_app_dialog,
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="🗑️ Remove Selected", command=self.remove_selected_app,
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="🔄 Refresh", command=self.update_locked_apps_list,
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        # Apps list
        list_frame = tk.Frame(apps_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview
        columns = ("Name", "Type", "Path")
        self.apps_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.apps_tree.heading("Name", text="Application Name")
        self.apps_tree.heading("Type", text="Type")
        self.apps_tree.heading("Path", text="Path")
        
        self.apps_tree.column("Name", width=200)
        self.apps_tree.column("Type", width=80)
        self.apps_tree.column("Path", width=400)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.apps_tree.yview)
        self.apps_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.apps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Info label
        info_label = tk.Label(apps_frame, text="Double-click an app to edit, or use the toolbar buttons to manage protected applications.",
                             font=("Arial", 9), fg="gray")
        info_label.pack(pady=5)
    
    def create_settings_tab(self, notebook):
        """Create the settings tab"""
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="⚙️ Settings")
        
        # General settings
        general_frame = ttk.LabelFrame(settings_frame, text="General Settings", padding=10)
        general_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Checkbutton(general_frame, text="Stealth Mode (Hide from system tray)", 
                      variable=self.stealth_mode, 
                      command=self.update_settings,
                      font=("Arial", 10)).pack(anchor=tk.W, pady=2)
        
        tk.Checkbutton(general_frame, text="Log access attempts", 
                      variable=self.log_attempts, 
                      command=self.update_settings,
                      font=("Arial", 10)).pack(anchor=tk.W, pady=2)
        
        tk.Checkbutton(general_frame, text="Start with Windows", 
                      variable=self.startup_with_windows, 
                      command=self.update_startup_setting,
                      font=("Arial", 10)).pack(anchor=tk.W, pady=2)
        
        # Timeout setting
        timeout_frame = tk.Frame(general_frame)
        timeout_frame.pack(anchor=tk.W, pady=5)
        
        tk.Label(timeout_frame, text="Password dialog timeout:", 
                font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.timeout_var = tk.StringVar(value=str(self.config_manager.get_setting('auto_close_timeout', 15)))
        timeout_spinbox = tk.Spinbox(timeout_frame, from_=5, to=60, width=5, 
                                   textvariable=self.timeout_var,
                                   command=self.update_timeout)
        timeout_spinbox.pack(side=tk.LEFT, padx=5)
        
        tk.Label(timeout_frame, text="seconds", 
                font=("Arial", 10)).pack(side=tk.LEFT)
        
        # Security settings
        security_frame = ttk.LabelFrame(settings_frame, text="Security", padding=10)
        security_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(security_frame, text="🔑 Change Master Password", 
                 command=self.change_password, width=20,
                 font=("Arial", 10)).pack(pady=5)
        
        # Database management
        db_frame = ttk.LabelFrame(settings_frame, text="Data Management", padding=10)
        db_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(db_frame, text="🗑️ Clear All Logs", 
                 command=self.clear_logs, width=20,
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(db_frame, text="💾 Export Settings", 
                 command=self.export_settings, width=20,
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    def create_logs_tab(self, notebook):
        """Create the access logs tab"""
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="📊 Access Logs")
        
        # Toolbar
        logs_toolbar = tk.Frame(logs_frame)
        logs_toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(logs_toolbar, text="🔄 Refresh", command=self.update_logs,
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        tk.Button(logs_toolbar, text="🗑️ Clear Logs", command=self.clear_logs,
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        # Logs list
        logs_list_frame = tk.Frame(logs_frame)
        logs_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for logs
        log_columns = ("Time", "Application", "Status", "User")
        self.logs_tree = ttk.Treeview(logs_list_frame, columns=log_columns, show="headings", height=20)
        
        # Configure columns
        self.logs_tree.heading("Time", text="Access Time")
        self.logs_tree.heading("Application", text="Application")
        self.logs_tree.heading("Status", text="Status")
        self.logs_tree.heading("User", text="User")
        
        self.logs_tree.column("Time", width=150)
        self.logs_tree.column("Application", width=200)
        self.logs_tree.column("Status", width=100)
        self.logs_tree.column("User", width=100)
        
        # Scrollbar for logs
        logs_scrollbar = ttk.Scrollbar(logs_list_frame, orient=tk.VERTICAL, command=self.logs_tree.yview)
        self.logs_tree.configure(yscrollcommand=logs_scrollbar.set)
        
        # Pack logs treeview and scrollbar
        self.logs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.update_logs()
    
    def toggle_protection(self):
        """Toggle protection on/off"""
        enabled = self.protection_enabled.get()
        self.config_manager.set_setting('protection_enabled', enabled)
        self.update_status()
        
        status = "enabled" if enabled else "disabled"
        messagebox.showinfo("AppLock", f"Protection has been {status}.")
    
    def update_status(self):
        """Update the status display"""
        if self.protection_enabled.get():
            locked_count = len(self.config_manager.get_locked_apps())
            self.status_label.config(text=f"🟢 Protection ENABLED - {locked_count} apps protected", 
                                   fg="green")
        else:
            self.status_label.config(text="🔴 Protection DISABLED", fg="red")
    
    def set_password(self):
        """Show dialog to set the master password"""
        dialog = PasswordSetDialog(self.root, self.config_manager)
        dialog.show()
        
        if not self.config_manager.has_password():
            messagebox.showerror("Error", "AppLock requires a master password to function.")
            self.root.quit()
    
    def change_password(self):
        """Show dialog to change the master password"""
        if self.config_manager.has_password():
            # Verify current password first
            from utils.system_utils import PasswordDialog
            dialog = PasswordDialog("Current Password Verification")
            current_password = dialog.show()
            
            if not current_password or not self.config_manager.verify_password(current_password):
                messagebox.showerror("Error", "Incorrect current password.")
                return
        
        # Show new password dialog
        dialog = PasswordSetDialog(self.root, self.config_manager, is_change=True)
        dialog.show()
    
    def add_app_dialog(self):
        """Show dialog to add a new app to protection"""
        dialog = AddAppDialog(self.root, self.config_manager)
        if dialog.show():
            self.update_locked_apps_list()
    
    def remove_selected_app(self):
        """Remove selected app from protection"""
        selection = self.apps_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an app to remove.")
            return
        
        item = self.apps_tree.item(selection[0])
        app_name = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Remove '{app_name}' from protected apps?"):
            # Get the app ID (stored as tag)
            app_id = int(self.apps_tree.item(selection[0], 'tags')[0])
            
            if self.config_manager.remove_locked_app(app_id):
                self.update_locked_apps_list()
                messagebox.showinfo("Success", f"'{app_name}' has been removed from protection.")
            else:
                messagebox.showerror("Error", "Failed to remove the application.")
    
    def update_locked_apps_list(self):
        """Update the locked apps list display"""
        # Clear existing items
        for item in self.apps_tree.get_children():
            self.apps_tree.delete(item)
        
        # Add locked apps
        locked_apps = self.config_manager.get_locked_apps()
        for app in locked_apps:
            self.apps_tree.insert("", tk.END, 
                                values=(app['app_name'], app['app_type'].upper(), app['app_path']),
                                tags=(str(app['id']),))
        
        self.update_status()
    
    def update_settings(self):
        """Update settings when checkboxes change"""
        self.config_manager.set_setting('stealth_mode', self.stealth_mode.get())
        self.config_manager.set_setting('log_attempts', self.log_attempts.get())
    
    def update_startup_setting(self):
        """Update Windows startup setting"""
        add_to_startup(self.startup_with_windows.get())
    
    def update_timeout(self):
        """Update password dialog timeout setting"""
        try:
            timeout = int(self.timeout_var.get())
            self.config_manager.set_setting('auto_close_timeout', timeout)
        except ValueError:
            pass
    
    def update_logs(self):
        """Update the access logs display"""
        # Clear existing items
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)
        
        # Add logs
        logs = self.config_manager.get_access_logs()
        for log in logs:
            status = "✅ GRANTED" if log['access_granted'] else "❌ DENIED"
            self.logs_tree.insert("", tk.END, values=(
                log['access_time'],
                log['app_name'],
                status,
                log['user_name'] or "Unknown"
            ))
    
    def clear_logs(self):
        """Clear all access logs"""
        if messagebox.askyesno("Confirm", "Clear all access logs?"):
            # This would need to be implemented in ConfigManager
            messagebox.showinfo("Info", "Logs cleared (feature to be implemented).")
    
    def export_settings(self):
        """Export settings to file"""
        messagebox.showinfo("Info", "Export feature to be implemented.")
    
    def run(self):
        """Run the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        if self.config_manager.get_setting('stealth_mode', False):
            # Minimize to system tray instead of closing
            self.root.withdraw()
        else:
            self.app_monitor.stop_monitoring()
            self.root.quit()


class PasswordSetDialog:
    """Dialog for setting the master password"""
    
    def __init__(self, parent, config_manager, is_change=False):
        self.parent = parent
        self.config_manager = config_manager
        self.is_change = is_change
        self.result = False
    
    def show(self):
        """Show the password setup dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Set Master Password" if not self.is_change else "Change Master Password")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content
        tk.Label(dialog, text="🔑 Master Password Setup", 
                font=("Arial", 16, "bold")).pack(pady=20)
        
        info_text = "Set a master password to protect your applications." if not self.is_change else "Enter a new master password."
        tk.Label(dialog, text=info_text, 
                font=("Arial", 10)).pack(pady=10)
        
        # Password fields
        tk.Label(dialog, text="Password:", font=("Arial", 10)).pack(pady=5)
        password_var = tk.StringVar()
        password_entry = tk.Entry(dialog, textvariable=password_var, show="*", 
                                font=("Arial", 12), width=25)
        password_entry.pack(pady=5)
        password_entry.focus()
        
        tk.Label(dialog, text="Confirm Password:", font=("Arial", 10)).pack(pady=5)
        confirm_var = tk.StringVar()
        confirm_entry = tk.Entry(dialog, textvariable=confirm_var, show="*", 
                               font=("Arial", 12), width=25)
        confirm_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def on_ok():
            password = password_var.get()
            confirm = confirm_var.get()
            
            if not password:
                messagebox.showerror("Error", "Password cannot be empty.")
                return
            
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match.")
                return
            
            if len(password) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters long.")
                return
            
            if self.config_manager.set_password(password):
                self.result = True
                dialog.destroy()
                messagebox.showinfo("Success", "Master password has been set successfully.")
            else:
                messagebox.showerror("Error", "Failed to set password.")
        
        def on_cancel():
            dialog.destroy()
        
        tk.Button(button_frame, text="OK", command=on_ok, 
                 font=("Arial", 10), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=on_cancel, 
                 font=("Arial", 10), width=10).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        password_entry.bind('<Return>', lambda e: confirm_entry.focus())
        confirm_entry.bind('<Return>', lambda e: on_ok())
        
        dialog.wait_window()
        return self.result


class AddAppDialog:
    """Dialog for adding applications to protection"""
    
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.result = False
    
    def show(self):
        """Show the add app dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Application to Protection")
        dialog.geometry("600x500")
        dialog.resizable(True, True)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Create notebook for different methods
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Browse for EXE tab
        browse_frame = ttk.Frame(notebook)
        notebook.add(browse_frame, text="📁 Browse for EXE")
        
        self.create_browse_tab(browse_frame)
        
        # Installed programs tab
        installed_frame = ttk.Frame(notebook)
        notebook.add(installed_frame, text="💻 Installed Programs")
        
        self.create_installed_tab(installed_frame, dialog)
        
        # UWP apps tab
        uwp_frame = ttk.Frame(notebook)
        notebook.add(uwp_frame, text="🏪 Store Apps")
        
        self.create_uwp_tab(uwp_frame, dialog)
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(button_frame, text="Close", command=dialog.destroy,
                 font=("Arial", 10)).pack(side=tk.RIGHT, padx=5)
        
        dialog.wait_window()
        return self.result
    
    def create_browse_tab(self, frame):
        """Create the browse for EXE tab"""
        tk.Label(frame, text="Browse for an executable file to protect:", 
                font=("Arial", 12)).pack(pady=20)
        
        self.selected_file_var = tk.StringVar()
        file_frame = tk.Frame(frame)
        file_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Entry(file_frame, textvariable=self.selected_file_var, 
                font=("Arial", 10), width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(file_frame, text="Browse...", 
                 command=self.browse_for_file,
                 font=("Arial", 10)).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(frame, text="Add Selected File", 
                 command=self.add_selected_file,
                 font=("Arial", 12), bg="lightgreen").pack(pady=20)
    
    def create_installed_tab(self, frame, dialog):
        """Create the installed programs tab"""
        tk.Label(frame, text="Select from installed programs:", 
                font=("Arial", 12)).pack(pady=10)
        
        # List of installed programs
        list_frame = tk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Name", "Path")
        self.installed_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        self.installed_tree.heading("Name", text="Program Name")
        self.installed_tree.heading("Path", text="Path")
        
        self.installed_tree.column("Name", width=250)
        self.installed_tree.column("Path", width=300)
        
        scrollbar_installed = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                          command=self.installed_tree.yview)
        self.installed_tree.configure(yscrollcommand=scrollbar_installed.set)
        
        self.installed_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_installed.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load installed programs
        self.load_installed_programs()
        
        # Add button
        tk.Button(frame, text="Add Selected Program", 
                 command=lambda: self.add_from_list(self.installed_tree, 'exe', dialog),
                 font=("Arial", 10)).pack(pady=10)
    
    def create_uwp_tab(self, frame, dialog):
        """Create the UWP apps tab"""
        tk.Label(frame, text="Select from Microsoft Store apps:", 
                font=("Arial", 12)).pack(pady=10)
        
        # List of UWP apps
        uwp_list_frame = tk.Frame(frame)
        uwp_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Name", "Package")
        self.uwp_tree = ttk.Treeview(uwp_list_frame, columns=columns, show="headings", height=15)
        
        self.uwp_tree.heading("Name", text="App Name")
        self.uwp_tree.heading("Package", text="Package Family Name")
        
        self.uwp_tree.column("Name", width=250)
        self.uwp_tree.column("Package", width=300)
        
        scrollbar_uwp = ttk.Scrollbar(uwp_list_frame, orient=tk.VERTICAL, 
                                    command=self.uwp_tree.yview)
        self.uwp_tree.configure(yscrollcommand=scrollbar_uwp.set)
        
        self.uwp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_uwp.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load UWP apps
        self.load_uwp_apps()
        
        # Add button
        tk.Button(frame, text="Add Selected App", 
                 command=lambda: self.add_from_list(self.uwp_tree, 'uwp', dialog),
                 font=("Arial", 10)).pack(pady=10)
    
    def browse_for_file(self):
        """Browse for an executable file"""
        file_path = filedialog.askopenfilename(
            title="Select Executable File",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if file_path:
            self.selected_file_var.set(file_path)
    
    def add_selected_file(self):
        """Add the selected file to protection"""
        file_path = self.selected_file_var.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a file first.")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Selected file does not exist.")
            return
        
        app_name = os.path.basename(file_path)
        if self.config_manager.add_locked_app(file_path, app_name, 'exe'):
            self.result = True
            messagebox.showinfo("Success", f"'{app_name}' has been added to protection.")
        else:
            messagebox.showerror("Error", "Failed to add the application.")
    
    def load_installed_programs(self):
        """Load installed programs in background"""
        def load_in_background():
            programs = get_installed_programs()
            for program in programs:
                self.installed_tree.insert("", tk.END, values=(program['name'], program['path']))
        
        threading.Thread(target=load_in_background, daemon=True).start()
    
    def load_uwp_apps(self):
        """Load UWP apps in background"""
        def load_in_background():
            apps = get_uwp_apps()
            for app in apps:
                self.uwp_tree.insert("", tk.END, 
                                   values=(app.get('name', 'Unknown'), 
                                         app.get('package_family_name', '')))
        
        threading.Thread(target=load_in_background, daemon=True).start()
    
    def add_from_list(self, tree, app_type, dialog):
        """Add selected app from list"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item first.")
            return
        
        item = tree.item(selection[0])
        app_name = item['values'][0]
        
        if app_type == 'exe':
            app_path = item['values'][1]
            package_family_name = None
        else:  # uwp
            app_path = app_name  # For UWP apps, we use the name as identifier
            package_family_name = item['values'][1]
        
        if self.config_manager.add_locked_app(app_path, app_name, app_type, package_family_name):
            self.result = True
            messagebox.showinfo("Success", f"'{app_name}' has been added to protection.")
            dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to add the application.")

"""
App Monitor for AppLock
Handles application launch interception and password prompt
"""

import time
import threading
from typing import List, Set, Dict
import psutil
import os
import subprocess
from .config_manager import ConfigManager
from utils.system_utils import prompt_for_password

class AppMonitor:
    """Monitors application launches and intercepts locked apps"""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.running = False
        self.seen_processes: Set[int] = set()
        self.monitoring_thread = None
        
        # Initialize with current processes to avoid false positives
        self._initialize_seen_processes()

    def _initialize_seen_processes(self):
        """Initialize the set of currently running processes"""
        try:
            for process in psutil.process_iter(['pid']):
                self.seen_processes.add(process.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def start_monitoring(self):
        """Start the monitoring process"""
        self.running = True
        print("AppLock monitoring started...")
        
        while self.running:
            if not self.config_manager.get_setting('protection_enabled', True):
                time.sleep(2)
                continue
                
            try:
                self._check_new_processes()
                self._check_uwp_apps()
            except Exception as e:
                print(f"Error in monitoring: {e}")
            
            time.sleep(0.5)  # Check every 500ms for better responsiveness

    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.running = False
        print("AppLock monitoring stopped.")

    def _check_new_processes(self):
        """Check for newly launched processes"""
        current_processes = set()
        locked_apps = self.config_manager.get_locked_apps()
        
        # Create lookup dictionary for faster access
        locked_paths = {app['app_path'].lower(): app for app in locked_apps if app['app_type'] == 'exe'}
        
        try:
            for process in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
                try:
                    process_info = process.info
                    pid = process_info['pid']
                    current_processes.add(pid)
                    
                    # Check if this is a new process
                    if pid not in self.seen_processes:
                        exe_path = process_info.get('exe')
                        if exe_path and exe_path.lower() in locked_paths:
                            app_info = locked_paths[exe_path.lower()]
                            
                            # Check if process was just created (within last 5 seconds)
                            create_time = process_info.get('create_time', 0)
                            if time.time() - create_time <= 5:
                                self._intercept_process(process, app_info)
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            print(f"Error checking processes: {e}")
        
        # Update seen processes
        self.seen_processes = current_processes

    def _check_uwp_apps(self):
        """Check for UWP/Microsoft Store app launches"""
        locked_apps = self.config_manager.get_locked_apps()
        uwp_apps = [app for app in locked_apps if app['app_type'] == 'uwp']
        
        if not uwp_apps:
            return
            
        try:
            # Use tasklist to check for UWP apps
            result = subprocess.run(['tasklist', '/fo', 'csv'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line:
                        parts = line.split('","')
                        if len(parts) >= 2:
                            process_name = parts[0].strip('"')
                            
                            for app in uwp_apps:
                                # Check if UWP app name matches
                                if app['app_name'].lower() in process_name.lower():
                                    # Additional verification could be added here
                                    # For now, we'll prompt for any matching UWP process
                                    pass
                                    
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception) as e:
            print(f"Error checking UWP apps: {e}")

    def _intercept_process(self, process: psutil.Process, app: dict):
        """Intercept the process launch and prompt for password"""
        try:
            app_name = app['app_name']
            app_path = app['app_path']
            
            print(f"Intercepting {app_name}...")
            
            # Get timeout setting
            timeout = self.config_manager.get_setting('auto_close_timeout', 15)
            
            # Prompt for password
            granted = prompt_for_password(app_name, timeout)
            
            # Log the attempt
            self.config_manager.log_access_attempt(
                app_name=app_name,
                app_path=app_path,
                access_granted=granted
            )
            
            if not granted:
                print(f"Access denied for {app_name}, terminating process...")
                try:
                    # Try to terminate gracefully first
                    process.terminate()
                    
                    # Wait a bit and force kill if still running
                    try:
                        process.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        process.kill()
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    print(f"Could not terminate {app_name} - insufficient permissions")
            else:
                print(f"Access granted for {app_name}")
                
        except Exception as e:
            print(f"Error intercepting process: {e}")

    def add_to_monitoring(self, app_path: str, app_name: str, app_type: str):
        """Add an application to real-time monitoring"""
        # This method can be used to dynamically add apps without restarting
        print(f"Added {app_name} to monitoring")

    def remove_from_monitoring(self, app_path: str):
        """Remove an application from real-time monitoring"""
        # This method can be used to dynamically remove apps without restarting
        print(f"Removed {app_path} from monitoring")

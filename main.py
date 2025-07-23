#!/usr/bin/env python3
"""
AppLock - Desktop Application Protection System for Windows
Main entry point for the application
"""

import sys
import os
import threading
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from gui.main_window import AppLockGUI
from core.app_monitor import AppMonitor
from core.config_manager import ConfigManager
from utils.system_utils import is_admin, run_as_admin

def main():
    """Main entry point for AppLock"""
    
    # Check if running as administrator (required for process monitoring)
    if not is_admin():
        print("AppLock requires administrator privileges to monitor applications.")
        print("Attempting to restart as administrator...")
        run_as_admin()
        return
    
    # Initialize configuration manager
    config_manager = ConfigManager()
    
    # Initialize app monitor
    app_monitor = AppMonitor(config_manager)
    
    # Start monitoring in background thread
    monitor_thread = threading.Thread(target=app_monitor.start_monitoring, daemon=True)
    monitor_thread.start()
    
    # Initialize and run GUI
    app = AppLockGUI(config_manager, app_monitor)
    app.run()

if __name__ == "__main__":
    main()

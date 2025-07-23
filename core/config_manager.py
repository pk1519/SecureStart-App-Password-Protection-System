"""
Configuration Manager for AppLock
Handles app settings, password storage, and locked apps configuration
"""

import json
import os
import bcrypt
from pathlib import Path
from typing import List, Dict, Any, Optional
import sqlite3
from datetime import datetime

class ConfigManager:
    """Manages AppLock configuration and settings"""
    
    def __init__(self):
        self.app_dir = Path.home() / "AppData" / "Local" / "AppLock"
        self.app_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.app_dir / "config.json"
        self.db_file = self.app_dir / "applock.db"
        
        self._init_database()
        self._load_config()
    
    def _init_database(self):
        """Initialize SQLite database for storing configuration"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS locked_apps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_path TEXT NOT NULL,
                app_name TEXT NOT NULL,
                app_type TEXT NOT NULL,  -- 'exe' or 'uwp'
                package_family_name TEXT,  -- for UWP apps
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT NOT NULL,
                app_path TEXT NOT NULL,
                access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_granted BOOLEAN NOT NULL,
                user_name TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_config(self):
        """Load configuration from file"""
        self.config = {
            "protection_enabled": True,
            "stealth_mode": False,
            "auto_close_timeout": 15,
            "log_attempts": True,
            "startup_with_windows": False
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def set_password(self, password: str) -> bool:
        """Set the master password with bcrypt hashing"""
        try:
            # Generate salt and hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Store hashed password
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', ('master_password_hash', hashed.decode('utf-8'), datetime.now()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error setting password: {e}")
            return False
    
    def verify_password(self, password: str) -> bool:
        """Verify the master password"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM settings WHERE key = ?', ('master_password_hash',))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False
            
            stored_hash = result[0].encode('utf-8')
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False
    
    def has_password(self) -> bool:
        """Check if a password is set"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM settings WHERE key = ?', ('master_password_hash',))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] > 0
        except Exception as e:
            print(f"Error checking password: {e}")
            return False
    
    def add_locked_app(self, app_path: str, app_name: str, app_type: str = 'exe', 
                      package_family_name: Optional[str] = None) -> bool:
        """Add an application to the locked apps list"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO locked_apps (app_path, app_name, app_type, package_family_name)
                VALUES (?, ?, ?, ?)
            ''', (app_path, app_name, app_type, package_family_name))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding locked app: {e}")
            return False
    
    def remove_locked_app(self, app_id: int) -> bool:
        """Remove an application from the locked apps list"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM locked_apps WHERE id = ?', (app_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error removing locked app: {e}")
            return False
    
    def get_locked_apps(self) -> List[Dict[str, Any]]:
        """Get list of all locked applications"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, app_path, app_name, app_type, package_family_name, is_active, created_at
                FROM locked_apps
                WHERE is_active = 1
                ORDER BY app_name
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            apps = []
            for row in rows:
                apps.append({
                    'id': row[0],
                    'app_path': row[1],
                    'app_name': row[2],
                    'app_type': row[3],
                    'package_family_name': row[4],
                    'is_active': bool(row[5]),
                    'created_at': row[6]
                })
            
            return apps
        except Exception as e:
            print(f"Error getting locked apps: {e}")
            return []
    
    def is_app_locked(self, app_path: str) -> bool:
        """Check if an application is locked"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM locked_apps 
                WHERE app_path = ? AND is_active = 1
            ''', (app_path,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] > 0
        except Exception as e:
            print(f"Error checking if app is locked: {e}")
            return False
    
    def log_access_attempt(self, app_name: str, app_path: str, access_granted: bool, user_name: str = None):
        """Log an access attempt"""
        if not self.config.get('log_attempts', True):
            return
        
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO access_logs (app_name, app_path, access_granted, user_name)
                VALUES (?, ?, ?, ?)
            ''', (app_name, app_path, access_granted, user_name or os.getlogin()))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging access attempt: {e}")
    
    def get_access_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent access logs"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT app_name, app_path, access_time, access_granted, user_name
                FROM access_logs
                ORDER BY access_time DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            logs = []
            for row in rows:
                logs.append({
                    'app_name': row[0],
                    'app_path': row[1],
                    'access_time': row[2],
                    'access_granted': bool(row[3]),
                    'user_name': row[4]
                })
            
            return logs
        except Exception as e:
            print(f"Error getting access logs: {e}")
            return []
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting"""
        return self.config.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Set a configuration setting"""
        self.config[key] = value
        self.save_config()
    
    def toggle_protection(self) -> bool:
        """Toggle protection on/off"""
        current = self.config.get('protection_enabled', True)
        self.set_setting('protection_enabled', not current)
        return not current

# 🛡️ AppLock - Desktop Application Protection System

A comprehensive Windows desktop application that provides password protection for any installed application, including both traditional EXE programs and modern UWP/Microsoft Store apps.

## ✨ Features

### 🔒 Core Protection Features
- **Application Interception**: Monitors and intercepts launches of protected applications
- **Password Authentication**: Secure bcrypt-hashed password system
- **Universal App Support**: Works with both EXE and UWP/Microsoft Store applications
- **Real-time Monitoring**: Continuous background monitoring with minimal resource usage

### 🖥️ User Interface
- **Intuitive GUI**: Clean, tabbed interface built with Tkinter
- **Easy App Management**: Browse for EXE files or select from installed programs
- **Live Status Display**: Real-time protection status and statistics
- **Comprehensive Logging**: Track all access attempts with timestamps

### ⚙️ Advanced Features
- **Stealth Mode**: Run hidden in the system tray
- **Windows Integration**: Optional startup with Windows
- **Configurable Timeouts**: Customizable password dialog timeout (5-60 seconds)
- **Access Control**: Toggle protection on/off with master switch
- **Secure Storage**: SQLite database with encrypted password storage

### 🎯 Bonus Features
- **Auto-termination**: Automatically closes unauthorized app launches
- **Comprehensive Logging**: Detailed access attempt logs with user information
- **Export/Import**: Settings backup and restore capabilities
- **Process Detection**: Smart detection of newly launched processes

## 🚀 Installation

### Prerequisites
- Windows 10/11
- Python 3.6 or higher
- Administrator privileges (required for process monitoring)

### Quick Setup

1. **Clone or download the AppLock folder to your desired location**

2. **Run the setup script as Administrator:**
   ```cmd
   python setup.py
   ```

3. **Or install dependencies manually:**
   ```cmd
   pip install psutil>=5.8.0 bcrypt>=3.2.0
   ```

## 📖 Usage

### First Run
1. **Launch AppLock as Administrator:**
   ```cmd
   python main.py
   ```

2. **Set Master Password**: On first launch, you'll be prompted to create a master password

3. **Add Applications**: Use the "Protected Apps" tab to add applications you want to protect

### Adding Applications

#### Method 1: Browse for EXE Files
- Click "Add App" → "Browse for EXE" tab
- Browse and select any .exe file
- Click "Add Selected File"

#### Method 2: Select from Installed Programs
- Click "Add App" → "Installed Programs" tab
- Choose from automatically detected installed applications
- Click "Add Selected Program"

#### Method 3: Microsoft Store Apps
- Click "Add App" → "Store Apps" tab
- Select from UWP/Microsoft Store applications
- Click "Add Selected App"

### Managing Protection

#### Enable/Disable Protection
- Use the "Enable Protection" checkbox on the Main tab
- Protection can be toggled without stopping the application

#### Change Master Password
- Go to Settings tab → "Change Master Password"
- Enter current password, then set new password

#### Configure Settings
- **Stealth Mode**: Hide AppLock from system tray
- **Auto-start**: Launch AppLock with Windows
- **Timeout**: Set password dialog timeout (5-60 seconds)
- **Logging**: Enable/disable access attempt logging

### Viewing Access Logs
- Go to "Access Logs" tab to view all access attempts
- See timestamps, application names, access status, and user information
- Refresh logs or clear history as needed

## 🔧 Configuration

### Settings File Location
```
%LOCALAPPDATA%\AppLock\
├── config.json          # Application settings
├── applock.db           # SQLite database (apps, logs, passwords)
```

### Default Configuration
```json
{
  "protection_enabled": true,
  "stealth_mode": false,
  "auto_close_timeout": 15,
  "log_attempts": true,
  "startup_with_windows": false
}
```

## 🛠️ Architecture

### Project Structure
```
AppLock/
├── main.py                 # Application entry point
├── setup.py               # Installation script
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
├── core/                 # Core functionality
│   ├── __init__.py
│   ├── config_manager.py  # Configuration and database management
│   └── app_monitor.py     # Process monitoring and interception
├── gui/                  # User interface
│   ├── __init__.py
│   └── main_window.py     # Main GUI application
└── utils/                # Utilities
    ├── __init__.py
    └── system_utils.py    # System integration and helpers
```

### Key Components

#### ConfigManager (`core/config_manager.py`)
- Handles all configuration settings
- Manages SQLite database operations
- Secure password hashing with bcrypt
- Application and log management

#### AppMonitor (`core/app_monitor.py`)
- Real-time process monitoring
- Application launch interception
- UWP app detection and handling
- Process termination for unauthorized access

#### System Utils (`utils/system_utils.py`)
- Windows integration functions
- Password dialog with timeout
- Registry operations for startup management
- Installed program detection

#### Main GUI (`gui/main_window.py`)
- Complete user interface
- Application management dialogs
- Settings configuration
- Access log viewing

## 🔐 Security Features

### Password Protection
- **bcrypt Hashing**: Industry-standard password hashing
- **Salt Generation**: Unique salt for each password
- **Secure Storage**: Passwords never stored in plain text

### Process Monitoring
- **Real-time Detection**: Monitors new process creation
- **Permission Checks**: Requires administrator privileges
- **Safe Termination**: Graceful process termination with fallback

### Privacy
- **Local Storage**: All data stored locally on user's machine
- **No Network Access**: No internet connection required or used
- **User Control**: Complete control over protected applications

## ⚡ Performance

### Resource Usage
- **Low CPU**: Efficient process monitoring (~0.5s intervals)
- **Minimal Memory**: Small memory footprint
- **Background Operation**: Runs silently in background

### Optimization Features
- **Smart Caching**: Caches process lists for faster lookups
- **Efficient Queries**: Optimized database operations
- **Lazy Loading**: UI components loaded as needed

## 🚨 Troubleshooting

### Common Issues

#### "Administrator privileges required"
- **Solution**: Always run AppLock as Administrator
- **Why**: Process monitoring requires elevated permissions

#### "Cannot detect UWP apps"
- **Solution**: Ensure PowerShell execution policy allows scripts
- **Command**: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

#### "Password dialog not appearing"
- **Check**: Ensure protection is enabled
- **Verify**: Application is in protected apps list
- **Test**: Try with a simple .exe application first

#### "App still launches despite protection"
- **Verify**: AppLock is running as Administrator
- **Check**: Process was detected within 5-second window
- **Consider**: Some apps may have multiple processes

### Debug Mode
To enable debug output, modify the monitoring functions to include print statements or check the console output when running from command line.

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install development dependencies
3. Run tests (when implemented)
4. Submit pull requests

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document all public methods
- Include error handling

## 📄 License

This project is provided as-is for educational and personal use. Please review and comply with all applicable laws and regulations when using application control software.

## 🙏 Acknowledgments

- **psutil**: Cross-platform process monitoring
- **bcrypt**: Secure password hashing
- **tkinter**: Built-in Python GUI framework
- **sqlite3**: Lightweight database for local storage

## 📞 Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Review the code documentation
3. Test with simple applications first
4. Ensure proper administrator privileges

contact me --priyanshu345kumar@gmail.com
---

**⚠️ Important Security Note**: AppLock is designed as a convenience tool and should not be relied upon as the sole security measure for sensitive applications. It can be bypassed by users with sufficient technical knowledge and administrator privileges.

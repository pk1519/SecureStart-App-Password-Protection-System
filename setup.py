"""
Setup script for AppLock
Installs dependencies and sets up the application
"""

import sys
import subprocess
import os
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    print("Installing required packages...")
    
    requirements = [
        "psutil>=5.8.0",
        "bcrypt>=3.2.0"
    ]
    
    for requirement in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
            print(f"✓ Installed {requirement}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {requirement}: {e}")
            return False
    
    return True

def create_desktop_shortcut():
    """Create a desktop shortcut for AppLock"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "AppLock.lnk")
        target = str(Path(__file__).parent / "main.py")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = str(Path(__file__).parent)
        shortcut.IconLocation = sys.executable
        shortcut.save()
        
        print(f"✓ Created desktop shortcut: {path}")
        return True
        
    except ImportError:
        print("⚠ Could not create desktop shortcut (winshell not available)")
        return False
    except Exception as e:
        print(f"✗ Failed to create desktop shortcut: {e}")
        return False

def setup_applock():
    """Main setup function"""
    print("🛡️ AppLock Setup")
    print("================")
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("✗ Python 3.6 or higher is required")
        return False
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install requirements
    if not install_requirements():
        print("✗ Failed to install requirements")
        return False
    
    # Try to create desktop shortcut
    create_desktop_shortcut()
    
    print("\n🎉 AppLock setup completed!")
    print("\nTo start AppLock:")
    print(f"  python \"{Path(__file__).parent / 'main.py'}\"")
    print("\nNote: AppLock requires administrator privileges to function properly.")
    
    return True

if __name__ == "__main__":
    success = setup_applock()
    
    if success:
        response = input("\nWould you like to start AppLock now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            try:
                subprocess.run([sys.executable, str(Path(__file__).parent / "main.py")])
            except Exception as e:
                print(f"Failed to start AppLock: {e}")
    
    input("\nPress Enter to exit...")

# 🚀 AppLock Quick Start Guide

## 📋 What You Need
- Windows 10/11
- Python 3.6+ installed
- Administrator privileges

## ⚡ Quick Installation

### Option 1: Automatic Setup (Recommended)
1. **Right-click on `run_applock.bat`** → **"Run as administrator"**
2. The system will automatically install dependencies if needed
3. Follow the on-screen setup prompts

### Option 2: Manual Setup
1. **Open Command Prompt as Administrator**
2. **Navigate to AppLock folder:**
   ```cmd
   cd path\to\AppLock
   ```
3. **Install dependencies:**
   ```cmd
   python -m pip install -r requirements.txt
   ```
4. **Run AppLock:**
   ```cmd
   python main.py
   ```

## 🔐 First Time Setup

### 1. Create Master Password
- On first launch, you'll see a password setup dialog
- Choose a strong password (minimum 4 characters)
- Confirm the password
- **Remember this password** - you'll need it to access protected apps!

### 2. Add Your First Protected App

#### Easy Method - Browse for File:
1. Click **"Add App"** button
2. Go to **"Browse for EXE"** tab  
3. Click **"Browse..."** and select any `.exe` file
4. Click **"Add Selected File"**

#### Smart Method - From Installed Programs:
1. Click **"Add App"** button
2. Go to **"Installed Programs"** tab
3. Wait for the list to load (may take a few seconds)
4. Select any program from the list
5. Click **"Add Selected Program"**

### 3. Test Protection
1. Make sure **"Enable Protection"** is checked ✅
2. Try to launch the protected application
3. You should see a password dialog appear
4. Enter your master password to proceed

## 🎯 Common Use Cases

### Protect Social Media Apps
```
1. Add apps like Discord, Teams, etc.
2. Perfect for workplace productivity
```

### Protect Gaming Applications  
```
1. Add Steam, game executables
2. Prevent accidental gaming during work
```

### Protect Financial Apps
```
1. Add banking software, trading apps
2. Extra security layer for sensitive data
```

### Protect System Tools
```
1. Add Registry Editor, Command Prompt
2. Prevent unauthorized system changes
```

## ⚙️ Essential Settings

### Enable Auto-Start (Recommended)
1. Go to **Settings** tab
2. Check ✅ **"Start with Windows"**
3. AppLock will automatically protect apps on startup

### Adjust Timeout
1. Go to **Settings** tab  
2. Change **"Password dialog timeout"** (5-60 seconds)
3. Shorter = more secure, Longer = more convenient

### Enable Stealth Mode
1. Go to **Settings** tab
2. Check ✅ **"Stealth Mode"**
3. AppLock will run hidden in background

## 🚨 Troubleshooting

### ❌ "Administrator privileges required"
**Solution:** Always run AppLock as Administrator
- Right-click `run_applock.bat` → "Run as administrator"
- Or run Command Prompt as Admin first

### ❌ Password dialog doesn't appear
**Check:**
- Is protection enabled? (Main tab checkbox)
- Is the app actually in your protected list?
- Try with a simple app like Notepad first

### ❌ App still opens without password
**Verify:**
- AppLock is running as Administrator
- The exact app path matches what's protected
- Protection isn't disabled in settings

### ❌ Can't find installed programs
**Wait:** The installed programs list takes time to load
**Alternative:** Use "Browse for EXE" method instead

## 💡 Pro Tips

### 🎯 **Start Small**
- Test with 1-2 apps first
- Add more once you're comfortable

### 🔄 **Regular Testing**  
- Periodically test your protected apps
- Ensure AppLock is working as expected

### 💾 **Backup Settings**
- Your settings are stored in: `%LOCALAPPDATA%\AppLock\`
- Copy this folder to backup your configuration

### 🔒 **Password Security**
- Use a strong but memorable password
- Don't use the same password for other accounts
- Consider using a password manager

### 📊 **Monitor Usage**
- Check the "Access Logs" tab regularly
- See when and how often apps are accessed
- Identify patterns in your usage

## 🆘 Need Help?

### Self-Help Checklist:
- [ ] Running as Administrator?
- [ ] Protection enabled?  
- [ ] App actually in protected list?
- [ ] Password correct?
- [ ] Tried with simple app (like Notepad)?

### Quick Test:
1. Add Notepad (`C:\Windows\System32\notepad.exe`)
2. Try to open Notepad from Start Menu
3. Password dialog should appear
4. If this works, AppLock is functioning correctly

---

**🛡️ You're ready to protect your applications!** 

Start with a few important apps, test the system, and gradually add more protection as needed. Remember: AppLock runs in the background, so you can close the main window and it will continue protecting your apps.

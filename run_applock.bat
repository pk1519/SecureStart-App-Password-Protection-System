@echo off
title AppLock - Application Protection System

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator...
    python "%~dp0main.py"
) else (
    echo AppLock requires Administrator privileges.
    echo Requesting elevation...
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d %~dp0 && python main.py && pause' -Verb RunAs"
)

pause

@echo off
echo.
echo ===================================================
echo    Flow Monitor - Windows Compatibility Check
echo ===================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Running compatibility check...
echo.

python windows_compatibility_check.py

if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo Ready to install! Run setup_windows.bat next.
    echo ===================================================
) else (
    echo.
    echo ===================================================
    echo Please fix the issues above before installation.
    echo See TROUBLESHOOTING_WINDOWS.md for help.
    echo ===================================================
)

pause
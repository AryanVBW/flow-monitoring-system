@echo off
REM Cross-Platform Flow Monitor Setup Script for Windows
REM This script installs all dependencies and sets up the environment

echo ============================================
echo   Cross-Platform Flow Monitor Setup
echo   Windows x64 Installation Script
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✓ Python found:
python --version

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)

echo ✓ pip found:
pip --version
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Check if installation was successful
echo.
echo Checking installation...
python -c "import serial; print('✓ pyserial installed')" 2>nul || echo "❌ pyserial failed"
python -c "import matplotlib; print('✓ matplotlib installed')" 2>nul || echo "❌ matplotlib failed"
python -c "import tkinter; print('✓ tkinter available')" 2>nul || echo "❌ tkinter failed"
python -c "import numpy; print('✓ numpy installed')" 2>nul || echo "❌ numpy failed"
python -c "import seaborn; print('✓ seaborn installed (optional)')" 2>nul || echo "⚠ seaborn not installed (optional)"

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo To run the Flow Monitor:
echo   python cross_platform_flow_monitor.py
echo.
echo To run the simple version:
echo   python simple_flow_gui.py
echo.
echo Make sure your Arduino is connected and
echo the SEN-HZ21WA sensor is properly wired.
echo.
pause
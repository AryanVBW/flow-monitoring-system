@echo off
REM Flow Monitoring System - Setup Script for Windows
REM This batch file launches the PowerShell setup script
REM For older systems or users who prefer CMD

title Flow Monitor - Setup

echo.
echo ============================================================
echo   Flow Monitoring System - Setup
echo   Windows Installer
echo ============================================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Launching PowerShell setup script...
    echo.
    powershell -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
    goto :end
)

REM Fallback: Direct installation without PowerShell
echo PowerShell not available. Running direct installation...
echo.

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist ".venv" (
    echo Removing existing virtual environment...
    rmdir /s /q ".venv"
)

python -m venv .venv
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

REM Activate and install dependencies
echo Activating virtual environment and installing dependencies...
call ".venv\Scripts\activate.bat"

python -m pip install --upgrade pip --quiet
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [OK] Dependencies installed
echo.

REM Verify installation
echo Verifying installation...
python -c "import serial; print('[OK] pyserial')"
python -c "import matplotlib; print('[OK] matplotlib')"
python -c "import numpy; print('[OK] numpy')"
python -c "import tkinter; print('[OK] tkinter')"
python -c "import seaborn; print('[OK] seaborn (optional)')" 2>nul || echo [WARN] seaborn not installed (optional)

echo.
echo ============================================================
echo   Setup Complete!
echo ============================================================
echo.
echo To run the Flow Monitor:
echo   run.bat
echo.
echo Make sure your Arduino is connected before starting!
echo.

:end
pause

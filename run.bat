@echo off
REM Flow Monitoring System - Run Script for Windows
REM Double-click this file to start the Flow Monitor

title Flow Monitor

echo.
echo ============================================
echo   Flow Monitor - Starting...
echo ============================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found.
    echo Running setup first...
    echo.
    call setup.bat
    if %ERRORLEVEL% NEQ 0 (
        echo Setup failed. Please check the error messages above.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call ".venv\Scripts\activate.bat"

REM Check dependencies
python -c "import serial, matplotlib, tkinter" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Missing dependencies. Installing...
    pip install -r requirements.txt
)

echo.
echo Launching Flow Monitor...
echo Tip: Connect your Arduino before clicking 'Connect'
echo.

REM Run the application
python src\core\cross_platform_flow_monitor.py %*

echo.
echo Flow Monitor closed.
pause

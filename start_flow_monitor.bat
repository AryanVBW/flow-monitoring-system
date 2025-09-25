@echo off
REM Flow Monitor Launcher for Windows
REM Double-click this file to start the Flow Monitor

title Flow Monitor - Starting...
echo.
echo ============================================
echo   🌊 Liquid Flow Monitor
echo   Starting Application...
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    echo After installing Python, run setup_windows.bat first
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import serial, matplotlib, tkinter" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Dependencies not installed!
    echo.
    echo Running setup_windows.bat to install dependencies...
    echo.
    call setup_windows.bat
    if errorlevel 1 (
        echo Setup failed. Please check the error messages above.
        pause
        exit /b 1
    )
)

REM Start the application
echo Starting Flow Monitor...
echo.
echo Instructions:
echo 1. Connect your Arduino with SEN-HZ21WA sensor
echo 2. Select the correct COM port in the application
echo 3. Click "Connect" to start monitoring
echo 4. Pour liquid through the sensor to see flow data
echo.
echo Close this window or press Ctrl+C to stop the application
echo.

REM Try to start the cross-platform version first
if exist cross_platform_flow_monitor.py (
    python cross_platform_flow_monitor.py
) else if exist simple_flow_gui.py (
    echo Cross-platform version not found, starting simple version...
    python simple_flow_gui.py
) else (
    echo ERROR: No Flow Monitor Python files found!
    echo Please ensure the following files are in this folder:
    echo - cross_platform_flow_monitor.py
    echo - simple_flow_gui.py
    echo.
    pause
    exit /b 1
)

echo.
echo Flow Monitor stopped.
pause
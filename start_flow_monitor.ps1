# Flow Monitor PowerShell Launcher
# Modern Windows PowerShell script for starting the Flow Monitor

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   🌊 Liquid Flow Monitor" -ForegroundColor Blue
Write-Host "   PowerShell Launcher" -ForegroundColor Blue
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check Python installation
if (-not (Test-Command "python")) {
    Write-Host "❌ ERROR: Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Display Python version
$pythonVersion = python --version 2>&1
Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green

# Check dependencies
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow

try {
    python -c "import serial, matplotlib, tkinter" 2>$null
    Write-Host "✅ All dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Dependencies missing, running setup..." -ForegroundColor Yellow
    
    if (Test-Path "requirements.txt") {
        Write-Host "Installing from requirements.txt..." -ForegroundColor Yellow
        pip install -r requirements.txt
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Setup failed. Please check error messages above." -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Host "❌ requirements.txt not found!" -ForegroundColor Red
        Write-Host "Please run setup_windows.bat first" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Start the application
Write-Host ""
Write-Host "🚀 Starting Flow Monitor..." -ForegroundColor Green
Write-Host ""
Write-Host "Instructions:" -ForegroundColor Cyan
Write-Host "1. Connect your Arduino with SEN-HZ21WA sensor" -ForegroundColor White
Write-Host "2. Select the correct COM port in the application" -ForegroundColor White
Write-Host "3. Click 'Connect' to start monitoring" -ForegroundColor White
Write-Host "4. Pour liquid through the sensor to see flow data" -ForegroundColor White
Write-Host ""

# Choose which version to run
if (Test-Path "cross_platform_flow_monitor.py") {
    Write-Host "Starting Cross-Platform Flow Monitor..." -ForegroundColor Green
    python cross_platform_flow_monitor.py
} elseif (Test-Path "simple_flow_gui.py") {
    Write-Host "Cross-platform version not found, starting simple version..." -ForegroundColor Yellow
    python simple_flow_gui.py
} else {
    Write-Host "❌ ERROR: No Flow Monitor Python files found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure the following files are in this folder:" -ForegroundColor Yellow
    Write-Host "- cross_platform_flow_monitor.py" -ForegroundColor White
    Write-Host "- simple_flow_gui.py" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Flow Monitor stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
#Requires -Version 5.1
<#
.SYNOPSIS
    Flow Monitoring System - Run Script for Windows
.DESCRIPTION
    Activates the virtual environment and launches the Flow Monitor application.
.EXAMPLE
    .\run.ps1
#>

$ErrorActionPreference = "Stop"

# Change to script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($scriptDir) {
    Set-Location $scriptDir
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🌊 Flow Monitoring System" -ForegroundColor White
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
$venvPath = ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "⚠ Virtual environment not found." -ForegroundColor Yellow
    Write-Host "Running setup first..." -ForegroundColor White
    Write-Host ""
    
    if (Test-Path "setup.ps1") {
        & .\setup.ps1
    }
    else {
        Write-Host "✗ setup.ps1 not found. Cannot continue." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "▶ Activating virtual environment..." -ForegroundColor Blue
$activateScript = ".\.venv\Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Host "✗ Virtual environment activation script not found." -ForegroundColor Red
    Write-Host "Please run setup.ps1 first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

& $activateScript
Write-Host "✓ Virtual environment active" -ForegroundColor Green

# Check dependencies
Write-Host "▶ Checking dependencies..." -ForegroundColor Blue
try {
    & python -c "import serial, matplotlib, tkinter" 2>&1 | Out-Null
    Write-Host "✓ Dependencies OK" -ForegroundColor Green
}
catch {
    Write-Host "⚠ Missing dependencies. Installing..." -ForegroundColor Yellow
    & pip install -r requirements.txt
}

# Launch application
Write-Host ""
Write-Host "🚀 Launching Flow Monitor..." -ForegroundColor Green
Write-Host "Tip: Connect your Arduino before clicking 'Connect'" -ForegroundColor Yellow
Write-Host ""

# Run the main application
& python src\core\cross_platform_flow_monitor.py $args

Write-Host ""
Write-Host "Flow Monitor closed." -ForegroundColor Green

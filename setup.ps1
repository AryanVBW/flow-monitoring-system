#Requires -Version 5.1
<#
.SYNOPSIS
    Flow Monitoring System - Universal Setup Script for Windows
.DESCRIPTION
    Creates virtual environment and installs all dependencies for the Flow Monitor.
    Compatible with Windows 10/11 with Python 3.8+
.EXAMPLE
    .\setup.ps1
#>

# Enable strict mode
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Colors
function Write-Header {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  🌊 Flow Monitoring System - Setup" -ForegroundColor White
    Write-Host "║  Universal Installer for Windows" -ForegroundColor Gray
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-Host "▶ $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Check Python installation
function Test-Python {
    Write-Step "Checking Python installation..."
    
    try {
        $pythonVersion = & python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
                Write-Error "Python 3.8+ required. Found: $pythonVersion"
                Write-Host ""
                Write-Host "Download Python from: https://python.org" -ForegroundColor Yellow
                Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
                return $false
            }
            
            Write-Success "Python $major.$minor found"
            return $true
        }
    }
    catch {
        Write-Error "Python not found!"
        Write-Host ""
        Write-Host "Download Python from: https://python.org" -ForegroundColor Yellow
        Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
        return $false
    }
    
    return $false
}

# Check tkinter
function Test-Tkinter {
    Write-Step "Checking tkinter (GUI library)..."
    
    try {
        & python -c "import tkinter" 2>&1 | Out-Null
        Write-Success "tkinter is available"
        return $true
    }
    catch {
        Write-Error "tkinter not available"
        Write-Host "tkinter should be included with Python on Windows." -ForegroundColor Yellow
        Write-Host "Try reinstalling Python from python.org" -ForegroundColor Yellow
        return $false
    }
}

# Create virtual environment
function New-VirtualEnvironment {
    Write-Step "Creating virtual environment..."
    
    $venvPath = ".venv"
    
    if (Test-Path $venvPath) {
        Write-Warning "Virtual environment already exists. Removing and recreating..."
        Remove-Item -Recurse -Force $venvPath
    }
    
    & python -m venv $venvPath
    
    if (-not (Test-Path $venvPath)) {
        Write-Error "Failed to create virtual environment"
        return $false
    }
    
    Write-Success "Virtual environment created at $venvPath\"
    return $true
}

# Activate virtual environment and install dependencies
function Install-Dependencies {
    Write-Step "Activating virtual environment..."
    
    $activateScript = ".\.venv\Scripts\Activate.ps1"
    
    if (-not (Test-Path $activateScript)) {
        Write-Error "Virtual environment activation script not found"
        return $false
    }
    
    # Activate the virtual environment
    & $activateScript
    Write-Success "Virtual environment activated"
    
    Write-Step "Upgrading pip..."
    & python -m pip install --upgrade pip --quiet
    
    Write-Step "Installing dependencies..."
    
    if (Test-Path "requirements.txt") {
        & pip install -r requirements.txt
        Write-Success "Dependencies installed from requirements.txt"
    }
    else {
        Write-Warning "requirements.txt not found. Installing core dependencies..."
        & pip install pyserial matplotlib numpy seaborn
        Write-Success "Core dependencies installed"
    }
    
    return $true
}

# Verify installation
function Test-Installation {
    Write-Step "Verifying installation..."
    
    $allOk = $true
    $modules = @("serial", "matplotlib", "numpy", "tkinter")
    
    foreach ($module in $modules) {
        try {
            & python -c "import $module" 2>&1 | Out-Null
            Write-Success $module
        }
        catch {
            Write-Error "$module - NOT INSTALLED"
            $allOk = $false
        }
    }
    
    # Optional: seaborn
    try {
        & python -c "import seaborn" 2>&1 | Out-Null
        Write-Success "seaborn (optional)"
    }
    catch {
        Write-Warning "seaborn not installed (optional)"
    }
    
    return $allOk
}

# Print completion message
function Write-Completion {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✅ Setup Complete!" -ForegroundColor White
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "To run the Flow Monitor:" -ForegroundColor White
    Write-Host "  .\run.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or use the batch file:" -ForegroundColor White
    Write-Host "  run.bat" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Make sure your Arduino is connected before starting!" -ForegroundColor Yellow
}

# Main execution
function Main {
    # Change to script directory
    $scriptDir = Split-Path -Parent $MyInvocation.ScriptName
    if ($scriptDir) {
        Set-Location $scriptDir
    }
    
    Write-Header
    
    if (-not (Test-Python)) {
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    if (-not (Test-Tkinter)) {
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    if (-not (New-VirtualEnvironment)) {
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    if (-not (Install-Dependencies)) {
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    if (-not (Test-Installation)) {
        Write-Error "Some dependencies failed to install"
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Completion
    Read-Host "Press Enter to exit"
}

Main

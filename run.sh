#!/usr/bin/env bash
#
# Flow Monitoring System - Run Script
# Compatible with: macOS, Ubuntu/Debian, and other Linux distributions
#
# Usage: ./run.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  🌊 ${GREEN}Flow Monitoring System${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if virtual environment exists
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found.${NC}"
    echo -e "Running setup first..."
    echo ""
    
    if [ -f "setup.sh" ]; then
        chmod +x setup.sh
        ./setup.sh
    else
        echo -e "${RED}✗ setup.sh not found. Cannot continue.${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${BLUE}▶${NC} Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓${NC} Virtual environment active"

# Check pip-installed dependencies (not tkinter - it's a system package)
echo -e "${BLUE}▶${NC} Checking dependencies..."
if ! python -c "import serial, matplotlib" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Missing dependencies. Running setup...${NC}"
    pip install -r requirements.txt
fi
echo -e "${GREEN}✓${NC} Dependencies OK"

# Launch application
echo ""
echo -e "${GREEN}🚀 Launching Flow Monitor...${NC}"
echo -e "${YELLOW}Tip: Connect your Arduino before clicking 'Connect'${NC}"
echo ""

# Run the main application
python src/core/cross_platform_flow_monitor.py "$@"

# Deactivate on exit
deactivate 2>/dev/null || true
echo ""
echo -e "${GREEN}Flow Monitor closed.${NC}"

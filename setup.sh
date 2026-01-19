#!/usr/bin/env bash
#
# Flow Monitoring System - Universal Setup Script
# Compatible with: macOS, Ubuntu/Debian, and other Linux distributions
#
# Usage: ./setup.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  🌊 ${GREEN}Flow Monitoring System - Setup${NC}"
    echo -e "${BLUE}║${NC}  Universal Installer for macOS/Linux"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"
}

print_step() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Detect OS
detect_os() {
    print_step "Detecting operating system..."
    
    case "$(uname -s)" in
        Darwin*)
            OS="macOS"
            PACKAGE_MANAGER="brew"
            ;;
        Linux*)
            if [ -f /etc/debian_version ]; then
                OS="Ubuntu/Debian"
                PACKAGE_MANAGER="apt-get"
            elif [ -f /etc/redhat-release ]; then
                OS="RHEL/CentOS"
                PACKAGE_MANAGER="yum"
            elif [ -f /etc/arch-release ]; then
                OS="Arch Linux"
                PACKAGE_MANAGER="pacman"
            else
                OS="Linux"
                PACKAGE_MANAGER="unknown"
            fi
            ;;
        *)
            print_error "Unsupported operating system: $(uname -s)"
            exit 1
            ;;
    esac
    
    print_success "Detected: $OS ($(uname -m))"
}

# Check Python installation
check_python() {
    print_step "Checking Python installation..."
    
    # Try python3 first, then python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python not found!"
        echo ""
        if [ "$OS" = "macOS" ]; then
            echo "Install Python with: brew install python3"
            echo "Or download from: https://python.org"
        elif [ "$PACKAGE_MANAGER" = "apt-get" ]; then
            echo "Install Python with: sudo apt-get install python3 python3-pip python3-venv"
        fi
        exit 1
    fi
    
    # Check version
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
    PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8+ required. Found: Python $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found ($PYTHON_CMD)"
}

# Check and install tkinter
check_tkinter() {
    print_step "Checking tkinter (GUI library)..."
    
    if $PYTHON_CMD -c "import tkinter" &> /dev/null; then
        print_success "tkinter is available"
        return 0
    else
        print_warning "tkinter not found"
        
        if [ "$OS" = "macOS" ]; then
            echo "   To install: brew install python-tk@3.14"
            echo "   Or reinstall Python with tkinter support"
        elif [ "$PACKAGE_MANAGER" = "apt-get" ]; then
            echo "   Installing python3-tk..."
            if sudo apt-get update && sudo apt-get install -y python3-tk; then
                print_success "tkinter installed"
                return 0
            fi
        elif [ "$PACKAGE_MANAGER" = "pacman" ]; then
            if sudo pacman -S --noconfirm tk; then
                print_success "tkinter installed"
                return 0
            fi
        fi
        
        echo ""
        print_warning "Continuing without tkinter - GUI may not work"
        return 0  # Continue anyway, user can fix later
    fi
}

# Create virtual environment
create_venv() {
    print_step "Creating virtual environment..."
    
    VENV_DIR=".venv"
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists. Removing and recreating..."
        rm -rf "$VENV_DIR"
    fi
    
    $PYTHON_CMD -m venv "$VENV_DIR"
    print_success "Virtual environment created at $VENV_DIR/"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_step "Installing dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip --quiet
    
    # Install from requirements.txt
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed from requirements.txt"
    else
        print_warning "requirements.txt not found. Installing core dependencies..."
        pip install pyserial matplotlib numpy seaborn
        print_success "Core dependencies installed"
    fi
}

# Verify installation
verify_installation() {
    print_step "Verifying installation..."
    
    ALL_OK=true
    
    # Check pip-installed dependencies
    for module in serial matplotlib numpy; do
        if $PYTHON_CMD -c "import $module" &> /dev/null; then
            print_success "$module"
        else
            print_error "$module - NOT INSTALLED"
            ALL_OK=false
        fi
    done
    
    # tkinter is a system library, check but don't fail
    if $PYTHON_CMD -c "import tkinter" &> /dev/null; then
        print_success "tkinter"
    else
        print_warning "tkinter not available (system library - install separately)"
    fi
    
    # Optional: seaborn
    if $PYTHON_CMD -c "import seaborn" &> /dev/null; then
        print_success "seaborn (optional)"
    else
        print_warning "seaborn not installed (optional)"
    fi
    
    if [ "$ALL_OK" = false ]; then
        print_error "Some dependencies failed to install"
        exit 1
    fi
}

# Make run script executable
setup_run_script() {
    print_step "Setting up run script..."
    
    if [ -f "run.sh" ]; then
        chmod +x run.sh
        print_success "run.sh is now executable"
    fi
}

# Print completion message
print_completion() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}  ✅ ${GREEN}Setup Complete!${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "To run the Flow Monitor:"
    echo -e "  ${BLUE}./run.sh${NC}"
    echo ""
    echo -e "Or activate the virtual environment manually:"
    echo -e "  ${BLUE}source .venv/bin/activate${NC}"
    echo -e "  ${BLUE}python src/core/cross_platform_flow_monitor.py${NC}"
    echo ""
    echo -e "Make sure your Arduino is connected before starting!"
}

# Main execution
main() {
    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    
    print_header
    detect_os
    check_python
    check_tkinter
    create_venv
    install_dependencies
    verify_installation
    setup_run_script
    print_completion
}

main "$@"

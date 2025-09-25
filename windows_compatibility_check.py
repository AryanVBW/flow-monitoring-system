"""
Windows System Compatibility Checker for Flow Monitor
Run this before installing the main application
"""
import sys
import os
import platform
import subprocess
import importlib
import serial.tools.list_ports

def print_header(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def print_status(item, status, details=""):
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {item}")
    if details:
        print(f"   {details}")

def check_system_info():
    print_header("SYSTEM INFORMATION")
    
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    
    # Check if 64-bit
    is_64bit = platform.machine().endswith('64')
    print_status("64-bit System", is_64bit, "Required for optimal performance")
    
    return is_64bit

def check_python():
    print_header("PYTHON INSTALLATION")
    
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    # Check version compatibility
    version_ok = version >= (3, 8)
    print_status("Python 3.8+", version_ok, f"Found {version.major}.{version.minor}")
    
    # Check if pip is available
    try:
        import pip
        pip_ok = True
        pip_version = pip.__version__
    except ImportError:
        pip_ok = False
        pip_version = "Not found"
    
    print_status("pip Package Manager", pip_ok, f"Version: {pip_version}")
    
    # Check if tkinter is available
    try:
        import tkinter
        tkinter_ok = True
    except ImportError:
        tkinter_ok = False
    
    print_status("tkinter GUI Library", tkinter_ok, "Required for GUI")
    
    return version_ok and pip_ok and tkinter_ok

def check_dependencies():
    print_header("PYTHON DEPENDENCIES")
    
    required_packages = [
        'serial',
        'matplotlib',
        'numpy',
        'threading',
        'logging'
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            if package == 'serial':
                import serial
                version = getattr(serial, '__version__', 'Unknown')
            elif package == 'threading':
                import threading
                version = "Built-in"
            elif package == 'logging':
                import logging
                version = "Built-in"
            else:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'Unknown')
            
            print_status(f"{package}", True, f"Version: {version}")
        except ImportError:
            print_status(f"{package}", False, "Not installed")
            all_ok = False
    
    return all_ok

def check_serial_ports():
    print_header("SERIAL PORTS")
    
    try:
        ports = list(serial.tools.list_ports.comports())
        
        if ports:
            print(f"Found {len(ports)} serial port(s):")
            for port in ports:
                print(f"  • {port.device}: {port.description}")
                if 'Arduino' in port.description or 'CH340' in port.description or 'FTDI' in port.description:
                    print(f"    👍 Likely Arduino device")
        else:
            print("❌ No serial ports found")
            print("   Make sure Arduino is connected via USB")
        
        return len(ports) > 0
    except Exception as e:
        print(f"❌ Error checking serial ports: {e}")
        return False

def check_windows_specific():
    print_header("WINDOWS-SPECIFIC CHECKS")
    
    # Check if running on Windows
    is_windows = platform.system() == 'Windows'
    print_status("Running on Windows", is_windows)
    
    if not is_windows:
        print("   This checker is designed for Windows systems")
        return False
    
    # Check Windows version
    win_version = platform.release()
    is_win10_or_later = win_version in ['10', '11'] or int(win_version.split('.')[0]) >= 10
    print_status("Windows 10 or later", is_win10_or_later, f"Found: Windows {win_version}")
    
    # Check for Visual C++ redistributables (for compiled packages)
    try:
        # Try to import a package that requires Visual C++
        import numpy
        vcredist_ok = True
    except ImportError:
        vcredist_ok = False
    
    print_status("Visual C++ Runtime", vcredist_ok, "Required for NumPy/Matplotlib")
    
    # Check PATH environment
    python_in_path = any('python' in path.lower() for path in os.environ.get('PATH', '').split(';'))
    print_status("Python in PATH", python_in_path, "Allows running 'python' from command line")
    
    return is_windows and is_win10_or_later

def run_compatibility_test():
    print("🔍 Windows Flow Monitor Compatibility Check")
    print("=" * 50)
    
    checks = []
    
    # Run all checks
    checks.append(("System", check_system_info()))
    checks.append(("Python", check_python()))
    checks.append(("Dependencies", check_dependencies()))
    checks.append(("Serial Ports", check_serial_ports()))
    checks.append(("Windows Features", check_windows_specific()))
    
    # Summary
    print_header("COMPATIBILITY SUMMARY")
    
    passed = sum(1 for _, status in checks if status)
    total = len(checks)
    
    for check_name, status in checks:
        print_status(check_name, status)
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Your system is fully compatible!")
        print("You can proceed with installing the Flow Monitor application.")
    elif passed >= 3:
        print("\n⚠️  Your system is mostly compatible.")
        print("You may encounter some issues. Check the failed items above.")
    else:
        print("\n❌ Your system needs attention before installation.")
        print("Please resolve the failed checks before proceeding.")
    
    print("\n" + "="*50)
    print("Next steps:")
    if passed == total:
        print("1. Run: setup_windows.bat")
        print("2. Launch: start_flow_monitor.bat")
    else:
        print("1. Fix the issues listed above")
        print("2. Run this checker again")
        print("3. See TROUBLESHOOTING_WINDOWS.md for help")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_compatibility_test()
        
        input("\nPress Enter to exit...")
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nCompatibility check cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your Python installation.")
        input("Press Enter to exit...")
        sys.exit(1)
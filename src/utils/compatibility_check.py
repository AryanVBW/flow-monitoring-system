#!/usr/bin/env python3
"""
Cross-Platform Compatibility Checker for Flow Monitor
Compatible with: Windows, macOS, and Linux

Run this before installing the main application to verify system compatibility.
"""

import sys
import os
import platform
import importlib


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*55}")
    print(f" {title}")
    print(f"{'='*55}")


def print_status(item: str, status: bool, details: str = "") -> None:
    """Print a status line with checkmark or X."""
    symbol = "✓" if status else "✗"
    print(f"{symbol} {item}")
    if details:
        print(f"   {details}")


def check_system_info() -> dict:
    """Check and display system information."""
    print_header("SYSTEM INFORMATION")

    system = platform.system()
    machine = platform.machine()
    release = platform.release()

    print(f"OS: {system} {release}")
    print(f"Architecture: {machine}")

    # Determine OS type
    if system == "Darwin":
        os_name = "macOS"
    elif system == "Windows":
        os_name = "Windows"
    elif system == "Linux":
        # Try to get distribution info
        try:
            import distro

            os_name = f"{distro.name()} {distro.version()}"
        except ImportError:
            if os.path.exists("/etc/debian_version"):
                os_name = "Debian/Ubuntu Linux"
            elif os.path.exists("/etc/redhat-release"):
                os_name = "RHEL/CentOS Linux"
            else:
                os_name = "Linux"
    else:
        os_name = system

    is_64bit = machine.endswith("64") or machine == "arm64"
    print_status("64-bit System", is_64bit, "Recommended for optimal performance")

    return {
        "system": system,
        "os_name": os_name,
        "machine": machine,
        "is_64bit": is_64bit,
        "ok": True,  # System info is informational, always OK
    }


def check_python() -> dict:
    """Check Python installation and version."""
    print_header("PYTHON INSTALLATION")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print(f"Python Version: {version_str}")
    print(f"Executable: {sys.executable}")

    # Check version >= 3.8
    version_ok = version >= (3, 8)
    print_status("Python 3.8+", version_ok, f"Found {version.major}.{version.minor}")

    # Check pip
    try:
        import pip

        pip_version = pip.__version__
        pip_ok = True
    except ImportError:
        pip_version = "Not found"
        pip_ok = False

    print_status("pip Package Manager", pip_ok, f"Version: {pip_version}")

    # Check tkinter
    try:
        import tkinter

        tkinter_ok = True
        tk_version = tkinter.TkVersion
    except ImportError:
        tkinter_ok = False
        tk_version = "Not available"

    print_status("tkinter GUI Library", tkinter_ok, f"Version: {tk_version}")

    if not tkinter_ok:
        system = platform.system()
        if system == "Linux":
            print("   Install with: sudo apt-get install python3-tk")
        elif system == "Darwin":
            print("   Reinstall Python with tkinter support")

    return {
        "version": version_str,
        "version_ok": version_ok,
        "pip_ok": pip_ok,
        "tkinter_ok": tkinter_ok,
        "ok": version_ok and pip_ok and tkinter_ok,
    }


def check_dependencies() -> dict:
    """Check if required Python packages are installed."""
    print_header("PYTHON DEPENDENCIES")

    required = {
        "serial": "pyserial",
        "matplotlib": "matplotlib",
        "numpy": "numpy",
    }

    optional = {
        "seaborn": "seaborn",
    }

    all_ok = True
    installed = []
    missing = []

    # Check required packages
    for import_name, package_name in required.items():
        try:
            module = importlib.import_module(import_name)
            version = getattr(module, "__version__", "Unknown")
            print_status(f"{package_name}", True, f"Version: {version}")
            installed.append(package_name)
        except ImportError:
            print_status(f"{package_name}", False, "Not installed")
            missing.append(package_name)
            all_ok = False

    # Check optional packages
    for import_name, package_name in optional.items():
        try:
            module = importlib.import_module(import_name)
            version = getattr(module, "__version__", "Unknown")
            print_status(f"{package_name} (optional)", True, f"Version: {version}")
            installed.append(package_name)
        except ImportError:
            print(f"⚠ {package_name} (optional) - Not installed")

    if missing:
        print(f"\n   Install missing packages: pip install {' '.join(missing)}")

    return {"installed": installed, "missing": missing, "ok": all_ok}


def check_serial_ports() -> dict:
    """Check available serial ports."""
    print_header("SERIAL PORTS")

    try:
        import serial.tools.list_ports

        ports = list(serial.tools.list_ports.comports())

        if ports:
            print(f"Found {len(ports)} serial port(s):")
            arduino_found = False
            for port in ports:
                print(f"  • {port.device}: {port.description}")
                # Check for common Arduino identifiers
                if any(
                    x in port.description.lower()
                    for x in ["arduino", "ch340", "ftdi", "usb serial", "usbserial"]
                ):
                    print(f"    ↳ Likely Arduino device")
                    arduino_found = True

            return {"ports": len(ports), "arduino_likely": arduino_found, "ok": True}
        else:
            print("⚠ No serial ports found")
            print("   Make sure Arduino is connected via USB")
            return {"ports": 0, "arduino_likely": False, "ok": False}

    except ImportError:
        print("✗ pyserial not installed - cannot check ports")
        return {"ports": 0, "arduino_likely": False, "ok": False}
    except Exception as e:
        print(f"✗ Error checking serial ports: {e}")
        return {"ports": 0, "arduino_likely": False, "ok": False}


def check_platform_specific() -> dict:
    """Run platform-specific checks."""
    system = platform.system()

    print_header(f"{system.upper()}-SPECIFIC CHECKS")

    if system == "Windows":
        # Windows-specific checks
        release = platform.release()
        is_win10_plus = release in ["10", "11"] or (
            release.isdigit() and int(release) >= 10
        )
        print_status("Windows 10+", is_win10_plus, f"Found: Windows {release}")

        # Check PATH
        python_in_path = any(
            "python" in p.lower() for p in os.environ.get("PATH", "").split(";")
        )
        print_status("Python in PATH", python_in_path)

        return {"ok": is_win10_plus}

    elif system == "Darwin":
        # macOS-specific checks
        mac_version = platform.mac_ver()[0]
        print(f"macOS Version: {mac_version}")

        # Check if Homebrew Python or system Python
        is_homebrew = (
            "/usr/local/" in sys.executable or "/opt/homebrew/" in sys.executable
        )
        print_status(
            "Using Homebrew Python", is_homebrew, "Recommended for best compatibility"
        )

        return {"mac_version": mac_version, "ok": True}

    elif system == "Linux":
        # Linux-specific checks
        print_status("Linux system detected", True)

        # Check for common package managers
        has_apt = os.path.exists("/usr/bin/apt-get")
        has_dnf = os.path.exists("/usr/bin/dnf")
        has_pacman = os.path.exists("/usr/bin/pacman")

        if has_apt:
            print("   Package manager: apt (Debian/Ubuntu)")
        elif has_dnf:
            print("   Package manager: dnf (Fedora/RHEL)")
        elif has_pacman:
            print("   Package manager: pacman (Arch)")

        return {"ok": True}

    return {"ok": True}


def run_compatibility_check() -> bool:
    """Run all compatibility checks and print summary."""
    print("\n🔍 Flow Monitor - Cross-Platform Compatibility Check")
    print("=" * 55)

    results = {}
    results["system"] = check_system_info()
    results["python"] = check_python()
    results["dependencies"] = check_dependencies()
    results["serial"] = check_serial_ports()
    results["platform"] = check_platform_specific()

    # Summary
    print_header("COMPATIBILITY SUMMARY")

    checks = [
        ("System", results["system"]["ok"]),
        ("Python", results["python"]["ok"]),
        ("Dependencies", results["dependencies"]["ok"]),
        ("Serial Ports", results["serial"]["ok"]),
        ("Platform", results["platform"]["ok"]),
    ]

    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)

    for name, ok in checks:
        print_status(name, ok)

    print(f"\nOverall: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 Your system is fully compatible!")
        print("You can proceed with running the Flow Monitor.")
    elif passed >= 3:
        print("\n⚠ Your system is mostly compatible.")
        print("Some features may not work. Check failed items above.")
    else:
        print("\n✗ Your system needs attention before use.")
        print("Please resolve the failed checks above.")

    print("\n" + "=" * 55)
    print("Next steps:")
    if passed >= 3:
        print("  macOS/Linux: ./run.sh")
        print("  Windows: run.bat or .\\run.ps1")
    else:
        print("  1. Fix the issues listed above")
        print("  2. Run this checker again")
        print("  3. See docs/TROUBLESHOOTING.md for help")

    return passed == total


def main():
    """Main entry point."""
    try:
        success = run_compatibility_check()

        # Wait for user input on Windows
        if platform.system() == "Windows":
            input("\nPress Enter to exit...")

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nCheck cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        print("Please check your Python installation.")
        sys.exit(1)


if __name__ == "__main__":
    main()

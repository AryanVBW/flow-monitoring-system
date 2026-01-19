#!/usr/bin/env python3
"""
Flow Monitoring System - Configuration
Centralized configuration constants for the entire application.
"""

import platform

# =============================================================================
# Serial Communication Settings
# =============================================================================
BAUD_RATE = 9600
CONNECTION_TIMEOUT = 10.0  # seconds
RECONNECT_INTERVAL = 5.0  # seconds

# =============================================================================
# Data Collection Settings
# =============================================================================
MAX_DATA_POINTS = 500  # Maximum points to keep in memory
PLOT_REFRESH_MS = 100  # Plot update interval in milliseconds
DATA_TIMEOUT_SECONDS = 5.0  # Mark data as stale after this duration

# =============================================================================
# Flow Sensor Settings (SEN-HZ21WA)
# =============================================================================
FLOW_MAX_REASONABLE = 50.0  # L/min - max expected flow rate
FLOW_MIN_REASONABLE = 0.0  # L/min - minimum flow rate
CALIBRATION_FACTOR = 7.5  # Pulses per liter per minute

# =============================================================================
# GUI Settings
# =============================================================================
WINDOW_TITLE = "Flow Monitoring System"
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

# =============================================================================
# Platform Detection
# =============================================================================
SYSTEM = platform.system()  # 'Windows', 'Darwin' (macOS), or 'Linux'
IS_WINDOWS = SYSTEM == "Windows"
IS_MACOS = SYSTEM == "Darwin"
IS_LINUX = SYSTEM == "Linux"

# =============================================================================
# Default Serial Port Patterns
# =============================================================================
if IS_WINDOWS:
    DEFAULT_PORT_PATTERN = "COM"
elif IS_MACOS:
    DEFAULT_PORT_PATTERN = "/dev/cu.usbserial"
else:  # Linux
    DEFAULT_PORT_PATTERN = "/dev/ttyUSB"

# =============================================================================
# Logging Settings
# =============================================================================
LOG_FILE = "flow_monitor.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# =============================================================================
# Version Info
# =============================================================================
VERSION = "2.0.0"
APP_NAME = "Flow Monitoring System"

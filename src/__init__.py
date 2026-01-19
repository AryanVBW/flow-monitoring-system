"""
Flow Monitoring System
A cross-platform Arduino-based liquid flow monitoring application.

Modules:
    core: Core monitoring functionality and main application
    gui: Graphical user interface components
    utils: Utility functions and compatibility checking
"""

__version__ = "2.0.0"
__author__ = "Flow Monitor Team"

from src.config import (
    VERSION,
    APP_NAME,
    BAUD_RATE,
    SYSTEM,
    IS_WINDOWS,
    IS_MACOS,
    IS_LINUX,
)

__all__ = [
    "__version__",
    "VERSION",
    "APP_NAME",
    "BAUD_RATE",
    "SYSTEM",
    "IS_WINDOWS",
    "IS_MACOS",
    "IS_LINUX",
]

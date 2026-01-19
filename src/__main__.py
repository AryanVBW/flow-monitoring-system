#!/usr/bin/env python3
"""
Flow Monitoring System - Package Entry Point
Allows running the package with: python -m src
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.cross_platform_flow_monitor import main

if __name__ == "__main__":
    main()

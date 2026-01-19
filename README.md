# Liquid Flow Monitoring System

A comprehensive Arduino-based liquid flow monitoring system using the SEN-HZ21WA water flow sensor with real-time data visualization.

**Compatible with:** macOS, Windows 10/11, and Ubuntu/Debian Linux

---

## ✨ Features

- **Accurate Flow Measurement** - Calibrated for SEN-HZ21WA sensor specifications
- **Real-time Visualization** - Live graphs showing flow rate and cumulative volume
- **Cross-Platform Support** - Works on macOS, Windows, and Linux
- **Automatic Port Detection** - Finds Arduino automatically
- **Data Export** - Save measurements to CSV format
- **Connection Monitoring** - Real-time sensor status tracking

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** - [Download Python](https://python.org)
- **Arduino** with SEN-HZ21WA sensor connected

### Installation

#### macOS / Linux (Ubuntu)
```bash
# Clone or download the project
cd flow-monitoring-system

# Run setup (creates virtual environment & installs dependencies)
chmod +x setup.sh
./setup.sh

# Start the application
./run.sh
```

#### Windows
```powershell
# Open PowerShell in project directory
.\setup.ps1

# Start the application
.\run.ps1
```

Or double-click `setup.bat` then `run.bat` for CMD users.

---

## 🔧 Hardware Setup

### Components Required
- Arduino Uno (or compatible)
- SEN-HZ21WA Water Flow Sensor
- USB cable (Type A to Type B)

### Wiring Diagram

```
SEN-HZ21WA Sensor    Arduino Uno
================     ===========
Red Wire (VCC)   →   5V
Black Wire (GND) →   GND
Yellow Wire      →   Digital Pin 2
```

> **Important:** Use Digital Pin 2 (interrupt-capable pin)

### Upload Arduino Code

1. Open `arduino/liquid_flow_monitor.ino` in Arduino IDE
2. Select your board: **Tools → Board → Arduino Uno**
3. Select port: **Tools → Port → (your Arduino)**
4. Click **Upload**

---

## 📁 Project Structure

```
flow-monitoring-system/
├── arduino/
│   └── liquid_flow_monitor.ino    # Arduino sketch
├── src/
│   ├── core/
│   │   └── cross_platform_flow_monitor.py  # Main application
│   ├── gui/
│   │   └── flow_monitor_gui.py    # GUI components
│   └── utils/
│       └── compatibility_check.py  # System checker
├── tests/
│   └── *.py                       # Test files
├── docs/                          # Documentation
├── setup.sh / setup.ps1 / setup.bat  # Setup scripts
├── run.sh / run.ps1 / run.bat        # Run scripts
├── requirements.txt               # Python dependencies
└── README.md
```

---

## 📊 Usage

1. **Connect Arduino** with sensor to USB
2. **Run the application** using `./run.sh` (macOS/Linux) or `run.bat` (Windows)
3. **Select COM port** from the dropdown and click **Connect**
4. **Start flowing liquid** through the sensor (minimum 1 L/min)
5. **Monitor** real-time flow rate and volume graphs

### Controls
- **Connect/Disconnect** - Toggle Arduino connection
- **Reset** - Clear all data
- **Export** - Save data to CSV

---

## 🔍 Troubleshooting

### Check Compatibility
Run the compatibility checker:
```bash
python src/utils/compatibility_check.py
```

### Common Issues

| Problem | Solution |
|---------|----------|
| Python not found | Install Python 3.8+ and add to PATH |
| tkinter missing | **Linux:** `sudo apt-get install python3-tk` |
| No serial ports | Check Arduino USB connection |
| No sensor reading | Verify wiring, ensure flow > 1 L/min |

---

## 📋 Requirements

- Python 3.8+
- pyserial
- matplotlib
- numpy
- tkinter (usually bundled with Python)
- seaborn (optional)

---

## 📄 License

This project is open source. Feel free to modify and distribute.

---

## 📝 Changelog

- **v2.0.0** - Complete restructure with cross-platform support
- **v1.2** - Real-time visualization and data export
- **v1.1** - Moving average filter and connection testing
- **v1.0** - Initial release

# Liquid Flow Monitoring System

A cross-platform Arduino-based liquid flow monitoring system with real-time data visualization.

**Compatible with:** macOS, Windows 10/11, and Ubuntu/Debian Linux

---

## ✨ Features

- **Real-time Flow Monitoring** - Live graphs showing flow rate and cumulative volume
- **Cross-Platform** - Works on macOS, Windows, and Linux
- **Auto Port Detection** - Automatically finds Arduino
- **Data Export** - Save measurements to CSV
- **Robust Error Handling** - Graceful connection management

---

## 🚀 Quick Start

### Prerequisites

| Platform | Requirements |
|----------|-------------|
| **All** | Python 3.8+, Arduino with SEN-HZ21WA sensor |
| **macOS** | `brew install python-tk` (if tkinter missing) |
| **Ubuntu** | `sudo apt-get install python3-tk` |
| **Windows** | Python from [python.org](https://python.org) with tcl/tk |

### Installation & Run

#### macOS / Linux
```bash
git clone https://github.com/AryanVBW/flow-monitoring-system.git
cd flow-monitoring-system
./setup.sh    # One-time setup
./run.sh      # Launch app
```

#### Windows (PowerShell)
```powershell
git clone https://github.com/AryanVBW/flow-monitoring-system.git
cd flow-monitoring-system
.\setup.ps1   # One-time setup
.\run.ps1     # Launch app
```

#### Windows (CMD)
Double-click `setup.bat` then `run.bat`

---

## 🔧 Hardware Setup

### Wiring

```
SEN-HZ21WA Sensor    Arduino Uno
================     ===========
Red Wire (VCC)   →   5V
Black Wire (GND) →   GND
Yellow Wire      →   Digital Pin 2 (interrupt-capable)
```

### Upload Arduino Code

1. Open `arduino/liquid_flow_monitor.ino` in Arduino IDE
2. Select **Tools → Board → Arduino Uno**
3. Select **Tools → Port → (your Arduino)**
4. Click **Upload**

---

## 📁 Project Structure

```
flow-monitoring-system/
├── arduino/
│   └── liquid_flow_monitor.ino     # Arduino sketch
├── src/
│   ├── core/
│   │   └── cross_platform_flow_monitor.py  # Main app
│   ├── gui/
│   │   └── flow_monitor_gui.py     # GUI components
│   └── utils/
│       └── compatibility_check.py  # System checker
├── tests/                          # Test files
├── docs/                           # Documentation
├── setup.sh | setup.ps1 | setup.bat   # Setup scripts
├── run.sh | run.ps1 | run.bat         # Run scripts
└── requirements.txt
```

---

## 📊 Usage

1. **Connect Arduino** to USB
2. **Run** `./run.sh` (macOS/Linux) or `run.bat` (Windows)
3. **Select port** from dropdown → Click **Connect**
4. **Flow liquid** through sensor (min 1 L/min)

### Controls
| Button | Action |
|--------|--------|
| Connect/Disconnect | Toggle connection |
| Refresh Ports | Rescan for devices |
| Export Data | Save to CSV |

---

## 🔍 Troubleshooting

| Problem | Solution |
|---------|----------|
| `tkinter not available` | macOS: `brew install python-tk` / Linux: `apt install python3-tk` |
| No serial ports found | Check USB cable, try different port |
| No flow reading | Check wiring, ensure flow > 1 L/min |
| Permission denied | Linux: `sudo usermod -a -G dialout $USER` then reboot |

### Run Compatibility Check
```bash
python src/utils/compatibility_check.py
```

---

## 📋 Requirements

- Python 3.8+
- pyserial, matplotlib, numpy
- tkinter (system library)
- seaborn (optional)

---

## 📄 License

Open source - free to modify and distribute.

---

## 📝 Changelog

| Version | Changes |
|---------|---------|
| **v2.0.0** | Complete restructure, cross-platform scripts |
| **v1.2** | Real-time visualization, data export |
| **v1.1** | Moving average filter, connection testing |
| **v1.0** | Initial release |

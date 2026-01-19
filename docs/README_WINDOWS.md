# 🌊 Cross-Platform Liquid Flow Monitor

A professional real-time liquid flow monitoring system with beautiful graphs, compatible with **Windows x64**, **macOS**, and **Linux**.

## 🎯 Features

- ✅ **Cross-platform compatibility** (Windows, macOS, Linux)
- ✅ **Real-time flow monitoring** with beautiful graphs
- ✅ **Automatic Arduino detection** and connection
- ✅ **Robust error handling** and recovery
- ✅ **Data export** to CSV format
- ✅ **Professional GUI** with menu system
- ✅ **High DPI support** on Windows
- ✅ **Comprehensive logging** for troubleshooting

## 🔧 Hardware Requirements

- **Arduino Uno** (or compatible)
- **SEN-HZ21WA Water Flow Sensor**
- **USB cable** for Arduino connection

### 🔌 Wiring Connections
```
SEN-HZ21WA  →  Arduino Uno
Red (VCC)   →  5V
Black (GND) →  GND
Yellow (Signal) → Digital Pin 2
```

## 💻 Software Requirements

### Windows x64
- **Python 3.8+** (Download from [python.org](https://python.org))
- **Windows 10/11** (Windows 7 may work but not tested)

### macOS
- **Python 3.8+** (included with macOS or via Homebrew)
- **macOS 10.14+**

### Linux
- **Python 3.8+**
- **tkinter** (`sudo apt-get install python3-tk` on Ubuntu/Debian)

## 🚀 Installation

### 📥 Method 1: Automatic Setup (Windows)

1. **Download** all files to a folder
2. **Double-click** `setup_windows.bat`
3. **Follow** the prompts
4. **Done!** Ready to run

### 📥 Method 2: Manual Setup (All Platforms)

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation:**
   ```bash
   python -c "import serial, matplotlib, tkinter; print('All dependencies installed!')"
   ```

## 🎮 Usage

### 🖥️ Cross-Platform GUI (Recommended)
```bash
python cross_platform_flow_monitor.py
```

**Features:**
- Professional menu system
- Automatic port detection
- Export data functionality
- Robust error handling
- Works on Windows, macOS, Linux

### 🎨 Simple GUI (Alternative)
```bash
python simple_flow_gui.py
```

**Features:**
- Simplified interface
- Beautiful seaborn styling
- Quick startup
- Good for basic monitoring

## 📊 What You'll See

The GUI displays two real-time graphs:

1. **📈 Flow Rate Graph** (Top)
   - Real-time flow rate in L/min
   - Blue line with smooth curves
   - Auto-scaling for optimal view

2. **📊 Volume Graph** (Bottom)
   - Cumulative volume in Liters
   - Red/purple line showing total
   - Integration of flow over time

3. **🔧 Status Information**
   - Connection status
   - Current flow rate and volume
   - Data points collected
   - System information

## 🛠️ Troubleshooting

### ❌ Common Issues

#### "No serial ports found"
- **Check:** Arduino USB connection
- **Try:** Different USB cable or port
- **Windows:** Check Device Manager for COM ports
- **macOS/Linux:** Check `/dev/tty*` or `/dev/cu*`

#### "Permission denied" (Linux/macOS)
```bash
sudo chmod 666 /dev/ttyUSB0  # or your port
# OR add user to dialout group:
sudo usermod -a -G dialout $USER
```

#### "Module not found" errors
```bash
pip install --upgrade -r requirements.txt
```

#### High flow rates without liquid
- **Normal:** Sensor is sensitive to vibrations
- **Fix:** Ensure stable mounting
- **Calibrate:** Use known liquid volume for testing

### 🔍 Advanced Debugging

1. **Check logs:** `flow_monitor.log` file
2. **Test Arduino:** Use serial monitor in Arduino IDE
3. **Port issues:** Try different USB ports
4. **Driver issues:** Install Arduino drivers

## 📝 Data Format

The system logs data in CSV format:
```
Time(ms),FlowRate(L/min),TotalVolume(L),Status,CurrentPulses,TotalPulses
1000,0.0000,0.00000,WAITING,0,0
2000,2.4000,0.00040,CONNECTED,18,18
```

## ⚙️ Calibration

The **SEN-HZ21WA** sensor specification:
- **7.5 Hz per L/min** (factory calibration)
- **Flow range:** 1-30 L/min
- **Accuracy:** ±3%

For custom calibration:
1. Measure exactly 1 liter of liquid
2. Pour through sensor at steady rate
3. Note pulse count and time
4. Adjust `CALIBRATION_FACTOR` in Arduino code

## 📁 File Structure

```
aku-project/
├── cross_platform_flow_monitor.py  # Main GUI (recommended)
├── simple_flow_gui.py              # Simple alternative GUI
├── liquid_flow_monitor.ino         # Arduino firmware
├── requirements.txt                 # Python dependencies
├── setup_windows.bat              # Windows auto-installer
├── README.md                       # This file
└── flow_monitor.log               # Application logs
```

## 🔄 Version History

- **v2.0** - Cross-platform support, enhanced GUI
- **v1.5** - Beautiful seaborn styling, improved parsing
- **v1.0** - Basic functionality, Arduino integration

## 🤝 Support

### 📧 Issues
- **Arduino not detected:** Check cables and drivers
- **High CPU usage:** Reduce plot refresh rate
- **Memory issues:** Clear data or restart application

### 🆘 Getting Help
1. Check the log file: `flow_monitor.log`
2. Test with Arduino Serial Monitor
3. Verify wiring connections
4. Check Python and dependency versions

## 🎉 Success Indicators

✅ **System Working When You See:**
- "Connected to Arduino" message
- Real-time data points updating
- Flow detection with liquid flow
- Graphs updating smoothly
- Status showing "CONNECTED" when liquid flows

## 📈 Performance Tips

### 🚀 For Best Performance:
- **Use USB 2.0 or 3.0** ports (avoid USB hubs)
- **Close other serial applications** (Arduino IDE Serial Monitor)
- **Ensure stable power** to Arduino
- **Mount sensor securely** to reduce vibration noise
- **Use quality USB cable** (avoid cheap cables)

## 🌟 Advanced Features

### 📊 Data Export
- Click **File → Export Data**
- Choose CSV format
- Import into Excel, MATLAB, etc.

### 🔌 Multiple Sensors
- Modify Arduino code for multiple pins
- Add sensor selection in GUI
- Use multiplexer for many sensors

### 📡 Remote Monitoring
- Log data to network drive
- Use VNC for remote GUI access
- Implement web interface (future feature)

---

**🌊 Happy Flow Monitoring! 🌊**
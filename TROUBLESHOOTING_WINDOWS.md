# 🛠️ Windows Troubleshooting Guide

## Common Windows Issues and Solutions

### 🔌 Arduino Connection Issues

#### Problem: "No serial ports found"
**Solutions:**
1. **Check Device Manager:**
   - Press `Win + X` → Device Manager
   - Look under "Ports (COM & LPT)"
   - Arduino should appear as "COM3", "COM4", etc.

2. **Install Arduino Drivers:**
   - Download from [arduino.cc](https://arduino.cc)
   - Right-click Arduino in Device Manager → Update Driver
   - Choose "Browse my computer for drivers"

3. **Try Different USB Port:**
   - Use USB 2.0 ports (more stable)
   - Avoid USB hubs
   - Try different USB cable

#### Problem: "Access denied" or "Permission denied"
**Solutions:**
1. **Close other applications:**
   - Arduino IDE Serial Monitor
   - PuTTY or other serial terminals
   - Other Python serial programs

2. **Run as Administrator:**
   - Right-click `start_flow_monitor.bat`
   - Choose "Run as administrator"

3. **Check Windows Defender:**
   - Add Python to exclusions
   - Disable real-time protection temporarily

### 🐍 Python Installation Issues

#### Problem: "Python is not recognized"
**Solutions:**
1. **Reinstall Python:**
   - Download from [python.org](https://python.org)
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install for all users"

2. **Manual PATH setup:**
   - Press `Win + R` → type `sysdm.cpl`
   - Advanced → Environment Variables
   - Add Python installation path to PATH

3. **Use Python Launcher:**
   - Try `py` instead of `python`
   - Example: `py cross_platform_flow_monitor.py`

#### Problem: "pip is not recognized"
**Solutions:**
1. **Reinstall Python** with pip included
2. **Manual pip installation:**
   ```cmd
   python -m ensurepip --upgrade
   ```

### 📦 Package Installation Issues

#### Problem: "Microsoft Visual C++ 14.0 is required"
**Solutions:**
1. **Install Visual Studio Build Tools:**
   - Download from Microsoft
   - Install "C++ build tools"

2. **Use pre-compiled wheels:**
   ```cmd
   pip install --only-binary=all -r requirements.txt
   ```

#### Problem: "Failed building wheel for xxx"
**Solutions:**
1. **Update pip and setuptools:**
   ```cmd
   python -m pip install --upgrade pip setuptools wheel
   ```

2. **Install packages individually:**
   ```cmd
   pip install pyserial
   pip install matplotlib
   pip install numpy
   ```

### 🖥️ Display Issues

#### Problem: "Tkinter not found" or GUI doesn't appear
**Solutions:**
1. **Reinstall Python** with tkinter included
2. **Check Python installation:**
   ```cmd
   python -c "import tkinter; print('Tkinter OK')"
   ```

#### Problem: Blurry or small GUI on high-DPI displays
**Solutions:**
1. The app automatically handles DPI awareness
2. **Manual fix:**
   - Right-click Python.exe
   - Properties → Compatibility
   - Check "Override high DPI scaling"

#### Problem: Graphs not displaying properly
**Solutions:**
1. **Update matplotlib:**
   ```cmd
   pip install --upgrade matplotlib
   ```

2. **Install additional backends:**
   ```cmd
   pip install pillow
   ```

### ⚡ Performance Issues

#### Problem: High CPU usage
**Solutions:**
1. **Reduce plot refresh rate** (edit PLOT_REFRESH_MS in code)
2. **Limit data points** (edit MAX_POINTS in code)
3. **Close other applications**

#### Problem: Application freezes
**Solutions:**
1. **Check Arduino connection** (LED should blink)
2. **Restart Arduino** (unplug/replug USB)
3. **Kill Python processes:**
   ```cmd
   taskkill /f /im python.exe
   ```

### 📊 Data Issues

#### Problem: Very high flow rates (>100 L/min) with no liquid
**Causes & Solutions:**
1. **Vibration sensitivity:**
   - Mount Arduino/sensor firmly
   - Avoid touching wires during operation
   - Keep sensor still

2. **Electrical noise:**
   - Use shorter wires
   - Add capacitor across sensor power (optional)
   - Keep away from motors/power supplies

3. **Calibration issues:**
   - Default: 7.5 Hz per L/min
   - Adjust CALIBRATION_FACTOR in Arduino code if needed

#### Problem: No data or "Waiting for data"
**Solutions:**
1. **Check Arduino code upload:**
   - Open Arduino IDE
   - Upload `liquid_flow_monitor.ino`
   - Check for upload errors

2. **Test Arduino separately:**
   - Open Arduino IDE Serial Monitor
   - Should see CSV data every second

3. **Check wiring:**
   ```
   SEN-HZ21WA → Arduino
   Red (VCC)  → 5V
   Black (GND) → GND
   Yellow     → Pin 2
   ```

### 🔧 Advanced Troubleshooting

#### Enable Debug Logging
Edit the Python file and change:
```python
logging.basicConfig(level=logging.DEBUG)
```

#### Manual Port Testing
```cmd
python -c "
import serial.tools.list_ports
for port in serial.tools.list_ports.comports():
    print(f'{port.device}: {port.description}')
"
```

#### Check Arduino Communication
```cmd
python -c "
import serial, time
ser = serial.Serial('COM3', 9600, timeout=2)  # Change COM3 to your port
for i in range(10):
    line = ser.readline().decode('utf-8').strip()
    if line: print(line)
    time.sleep(0.5)
ser.close()
"
```

### 🆘 Still Having Issues?

1. **Check the log file:** `flow_monitor.log`
2. **Test each component separately:**
   - Arduino code (Serial Monitor)
   - Python dependencies (`pip list`)
   - Serial communication (manual test)

3. **System information:**
   - Windows version: `winver`
   - Python version: `python --version`
   - Available COM ports: Device Manager

4. **Create a minimal test:**
   ```cmd
   python simple_flow_gui.py
   ```

### 📋 Pre-Flight Checklist

Before reporting issues, verify:
- ✅ Python 3.8+ installed with PATH
- ✅ All dependencies installed (`pip list`)
- ✅ Arduino appears in Device Manager
- ✅ Arduino code uploaded successfully
- ✅ No other serial applications running
- ✅ Proper wiring connections
- ✅ USB cable working (try different cable)

---

**💡 Most issues are solved by:**
1. Proper Python installation with PATH
2. Correct Arduino drivers
3. Closing conflicting serial applications
4. Using quality USB cables and ports
# Liquid Flow Measurement System

A comprehensive Arduino-based liquid flow monitoring system using the SEN-HZ21WA water flow sensor with real-time data visualization.

## Features

- **Accurate Flow Measurement**: Calibrated for SEN-HZ21WA sensor specifications
- **Stable Readings**: Moving average filter eliminates noise and fluctuations
- **Real-time Visualization**: Live graphs showing flow rate and cumulative volume
- **Connection Testing**: Automatic Arduino-PC connection verification
- **Low Power Design**: Optimized for USB power supply (no external power needed)
- **Data Logging**: Export measurements to CSV format
- **Status Monitoring**: Real-time sensor connection status

## Hardware Requirements

### Components
- Arduino Uno (or compatible)
- SEN-HZ21WA Water Flow Sensor
- USB cable (Type A to Type B)
- Jumper wires (optional, for breadboard connections)

### SEN-HZ21WA Specifications
- **Operating Voltage**: 5V DC
- **Flow Rate Range**: 1-30 L/min
- **Accuracy**: ±3%
- **Pulse Rate**: 7.5 pulses per liter per minute
- **Thread**: G1/2" (15mm)

## Wiring Diagram

```
SEN-HZ21WA Sensor    Arduino Uno
================     ===========
Red Wire (VCC)   ->  5V
Black Wire (GND) ->  GND
Yellow Wire (Signal) -> Digital Pin 2
```

**Important Notes:**
- Use Digital Pin 2 (interrupt-capable pin)
- Ensure secure connections
- Sensor requires minimum 1 L/min flow to generate pulses
- Maximum operating pressure: 1.75 MPa

## Software Setup

### Arduino IDE Setup

1. **Install Arduino IDE**
   - Download from [arduino.cc](https://www.arduino.cc/en/software)
   - Install for your operating system

2. **Upload the Code**
   - Open `liquid_flow_monitor.ino` in Arduino IDE
   - Select your Arduino board: Tools → Board → Arduino Uno
   - Select the correct port: Tools → Port → (your Arduino port)
   - Click Upload button (→)

3. **Test Connection**
   - Open Serial Monitor: Tools → Serial Monitor
   - Set baud rate to 9600
   - You should see initialization messages and connection test

### Python Visualization Setup

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or manually install:
   ```bash
   pip install pyserial matplotlib numpy
   ```

2. **Run the Visualization**
   ```bash
   python flow_monitor_gui.py
   ```

   Or specify a specific port:
   ```bash
   python flow_monitor_gui.py /dev/ttyACM0  # Linux/macOS
   python flow_monitor_gui.py COM3         # Windows
   ```

   While running, the top banner now independently tracks:

   - **Serial** — connection to the Arduino
   - **Data** — freshness of incoming samples (flags stale data after 5s)
   - **Sensor** — most recent sensor status message

   Use the bottom status strip to see runtime statistics, live flow rate/volume,
   and time since the latest update.

## Usage Instructions

### Initial Setup

1. **Hardware Assembly**
   - Connect the sensor according to the wiring diagram
   - Ensure all connections are secure
   - Connect Arduino to PC via USB

2. **Software Startup**
   - Upload Arduino code
   - Verify connection in Serial Monitor
   - Run Python visualization script

### Operation

1. **Starting Measurement**
   - Ensure liquid is flowing through the sensor
   - Minimum flow rate: 1 L/min for pulse generation
   - System will show "WAITING" until flow is detected

2. **Reading Data**
   - **Flow Rate**: Current flow in L/min (smoothed with moving average)
   - **Total Volume**: Cumulative volume since startup/reset
   - **Status**: WAITING/CONNECTED/DISCONNECTED

3. **Real-time Controls**
   - **Reset**: Clear all data and restart measurements
   - **Pause/Resume**: Stop/start data recording
   - **Save Data**: Export current data to CSV file

### Command-line Diagnostics

Use the enhanced CLI tester before launching the GUI to confirm data quality:

```bash
python connection_test_enhanced.py
```

- Auto-detects available serial ports and lets you choose interactively
- Verifies CSV output contains numeric flow and volume values
- Highlights stale or missing data so you can fix wiring or upload issues early

The quick tester (`quick_test.py`) remains available for a lightweight sanity check.

### Troubleshooting

#### No Sensor Reading
- Check wiring connections
- Ensure minimum flow rate (>1 L/min)
- Verify sensor orientation (arrow indicates flow direction)
- Check power supply (5V required)

#### Connection Issues
- Verify USB cable connection
- Check Arduino port in Device Manager (Windows) or System Preferences (macOS)
- Try different USB port
- Restart Arduino IDE and re-upload code

#### Erratic Readings
- Check for air bubbles in the system
- Ensure steady flow rate
- Verify sensor is properly sealed
- Consider increasing moving average sample size

## Calibration

The system is pre-calibrated for the SEN-HZ21WA sensor (7.5 pulses/L/min). For fine-tuning:

1. **Manual Calibration**
   - Measure exactly 1 liter using a measuring container
   - Note the pulse count during measurement
   - Adjust `CALIBRATION_FACTOR` in the Arduino code if needed

2. **Flow Rate Verification**
   - Use a known flow rate source
   - Compare readings with reference measurement
   - Adjust calibration factor accordingly

## Data Format

### Serial Output (CSV)
```
Time(ms),FlowRate(L/min),TotalVolume(L),Status
1000,2.500,0.0417,CONNECTED
2000,2.480,0.0834,CONNECTED
```

### Saved Data Format
```
Time(s),FlowRate(L/min),TotalVolume(L),Status
0.000,2.500,0.0417,CONNECTED
1.000,2.480,0.0834,CONNECTED
```

## Performance Specifications

- **Measurement Interval**: 1 second
- **Response Time**: <1 second
- **Accuracy**: ±3% (sensor limitation)
- **Resolution**: 0.001 L/min
- **Data Smoothing**: 10-point moving average
- **Max Display Points**: 300 (5 minutes at 1Hz)

## Advanced Features

### Moving Average Filter
- Reduces noise and provides stable readings
- Configurable sample size (default: 10 samples)
- Eliminates short-term fluctuations

### Connection Monitoring
- Automatic sensor connection detection
- Timeout-based disconnection detection (5 seconds)
- Visual status indicators

### Power Management
- Optimized for USB power supply
- Low power consumption design
- Built-in LED status indicator

## File Structure

```
aku-project/
├── liquid_flow_monitor.ino    # Main Arduino sketch
├── flow_monitor_gui.py        # Python visualization script
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Technical Details

### Arduino Code Structure
- **Interrupt-driven pulse counting**: Ensures no missed pulses
- **Moving average filtering**: Provides stable readings
- **Connection testing**: Verifies system integrity
- **CSV output format**: Easy data processing

### Python Visualization
- **Real-time plotting**: Live graphs with matplotlib
- **Thread-based data reading**: Non-blocking serial communication  
- **Data export**: CSV format for further analysis
- **Auto-port detection**: Simplified setup process

## Safety Considerations

- **Electrical Safety**: Ensure proper grounding and avoid water contact with electronics
- **Pressure Limits**: Do not exceed sensor maximum pressure (1.75 MPa)
- **Flow Direction**: Install sensor with arrow pointing in flow direction
- **Secure Mounting**: Ensure sensor is properly threaded and sealed

## Support and Maintenance

### Regular Maintenance
- Clean sensor threads and connections monthly
- Check for blockages or debris
- Verify calibration periodically with known flow rates

### Updates and Modifications
- Calibration factor can be adjusted for different sensor types
- Moving average sample size can be modified for different response characteristics
- Measurement interval can be changed for different applications

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Changelog

- **v1.0**: Initial release with basic flow measurement
- **v1.1**: Added moving average filter and connection testing
- **v1.2**: Implemented real-time visualization and data export# flow-monitoring-system

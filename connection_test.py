#!/usr/bin/env python3
"""
Arduino Connection Test Script
Simple script to test Arduino-PC connection and basic data reception

Usage: python connection_test.py [COM_PORT]
"""

import serial
import serial.tools.list_ports
import time
import sys

def find_arduino_ports():
    """Find all potential Arduino ports"""
    ports = serial.tools.list_ports.comports()
    arduino_ports = []
    
    for port in ports:
        if any(keyword in port.description.upper() for keyword in ['ARDUINO', 'CH340', 'USB', 'SERIAL']):
            arduino_ports.append(port)
    
    return arduino_ports

def test_connection(port_name, baudrate=9600, timeout=10):
    """Test connection to specified port"""
    print(f"Testing connection to {port_name}...")
    
    try:
        # Open serial connection
        ser = serial.Serial(port_name, baudrate, timeout=2)
        time.sleep(2)  # Wait for Arduino reset
        
        # Clear any buffered data
        ser.flushInput()
        
        print(f"✓ Serial connection established on {port_name}")
        print(f"  Baudrate: {baudrate}")
        print(f"  Timeout: {ser.timeout}s")
        
        # Test data reception
        print("\nWaiting for data from Arduino...")
        start_time = time.time()
        data_received = False
        
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        print(f"📊 Received: {line}")
                        data_received = True
                        
                        # Check if it's CSV data
                        if ',' in line and not line.startswith('==='):
                            parts = line.split(',')
                            if len(parts) >= 3:
                                try:
                                    flow_rate = float(parts[1])
                                    volume = float(parts[2])
                                    print(f"✓ Valid flow data - Rate: {flow_rate} L/min, Volume: {volume} L")
                                except ValueError:
                                    print("ℹ️  Non-numeric data (possibly header or status message)")
                        
                except UnicodeDecodeError:
                    print("⚠️  Received non-text data")
            
            time.sleep(0.1)
        
        if data_received:
            print(f"\n✅ Connection test PASSED for {port_name}")
            print("Arduino is responding and sending data")
        else:
            print(f"\n⚠️  Connection test PARTIAL for {port_name}")
            print("Serial connection works but no data received")
            print("Check if Arduino code is uploaded and sensor is connected")
        
        ser.close()
        return data_received
        
    except serial.SerialException as e:
        print(f"❌ Connection test FAILED for {port_name}")
        print(f"Error: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        if 'ser' in locals():
            ser.close()
        return False

def main():
    print("=== Arduino Connection Test ===")
    print("Testing Arduino-PC connection for Flow Monitor\n")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        port_name = sys.argv[1]
        print(f"Using specified port: {port_name}")
        test_connection(port_name)
    else:
        # Auto-detect and test all Arduino ports
        arduino_ports = find_arduino_ports()
        
        if not arduino_ports:
            print("❌ No Arduino ports found")
            print("\nTroubleshooting steps:")
            print("1. Ensure Arduino is connected via USB")
            print("2. Check if Arduino drivers are installed")
            print("3. Try a different USB cable")
            print("4. Check Device Manager (Windows) or System Information (macOS)")
            return
        
        print(f"Found {len(arduino_ports)} potential Arduino port(s):")
        for i, port in enumerate(arduino_ports):
            print(f"  {i+1}. {port.device} - {port.description}")
        
        print()
        
        # Test each port
        working_ports = []
        for port in arduino_ports:
            if test_connection(port.device):
                working_ports.append(port.device)
            print()  # Add spacing between tests
        
        # Summary
        print("=== Test Summary ===")
        if working_ports:
            print(f"✅ {len(working_ports)} working port(s) found:")
            for port in working_ports:
                print(f"  - {port}")
            print(f"\nTo use the flow monitor GUI:")
            print(f"python flow_monitor_gui.py {working_ports[0]}")
        else:
            print("❌ No working Arduino connections found")
            print("\nTroubleshooting:")
            print("1. Upload the Arduino sketch (liquid_flow_monitor.ino)")
            print("2. Check wiring connections")
            print("3. Verify Arduino power (LED should be on)")
            print("4. Try restarting Arduino IDE and re-uploading code")

if __name__ == "__main__":
    main()
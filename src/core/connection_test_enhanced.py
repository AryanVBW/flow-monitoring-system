#!/usr/bin/env python3
"""
Enhanced Arduino Connection Test with Port Selection
Simple script to test Arduino-PC connection with interactive port selection

Usage: python connection_test.py [COM_PORT]
"""

import serial
import serial.tools.list_ports
import time
import sys

def get_available_ports():
    """Get all available serial ports with detailed information"""
    ports = serial.tools.list_ports.comports()
    port_info = []
    
    for port in ports:
        # Categorize ports by type
        port_type = "Unknown"
        priority = 3
        
        if any(keyword in port.description.upper() for keyword in ['ARDUINO', 'UNO', 'NANO', 'MEGA']):
            port_type = "Arduino"
            priority = 1
        elif any(keyword in port.description.upper() for keyword in ['CH340', 'CH341', 'FTDI', 'CP210']):
            port_type = "USB-Serial"
            priority = 2
        elif 'USB' in port.description.upper():
            port_type = "USB Device"
            priority = 2
        elif 'BLUETOOTH' in port.description.upper():
            port_type = "Bluetooth"
            priority = 4
        
        port_info.append({
            'device': port.device,
            'description': port.description,
            'type': port_type,
            'priority': priority,
            'hwid': getattr(port, 'hwid', 'N/A')
        })
    
    # Sort by priority (Arduino first)
    port_info.sort(key=lambda x: (x['priority'], x['device']))
    return port_info

def select_port_interactive(ports):
    """Interactive port selection"""
    print("\n📋 Available Ports:")
    print("=" * 80)
    
    for i, port in enumerate(ports, 1):
        status_icon = "🔌" if port['type'] == "Arduino" else "📱" if port['type'] == "USB-Serial" else "🔗"
        print(f"  {i}. {status_icon} {port['device']:<20} | {port['type']:<12} | {port['description']}")
    
    print("=" * 80)
    
    # Auto-select Arduino if only one found
    arduino_ports = [p for p in ports if p['type'] == 'Arduino']
    if len(arduino_ports) == 1:
        arduino_index = next(i for i, p in enumerate(ports) if p['type'] == 'Arduino')
        print(f"✅ Auto-selecting Arduino: {arduino_ports[0]['device']}")
        return ports[arduino_index]['device']
    
    while True:
        try:
            choice = input(f"\n🎯 Select port (1-{len(ports)}) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                return None
            
            port_index = int(choice) - 1
            if 0 <= port_index < len(ports):
                selected_port = ports[port_index]['device']
                print(f"✅ Selected: {selected_port}")
                return selected_port
            else:
                print(f"❌ Invalid choice. Please enter 1-{len(ports)}")
                
        except ValueError:
            print("❌ Invalid input. Please enter a number or 'q'")
        except KeyboardInterrupt:
            print("\n🛑 Selection cancelled")
            return None

def test_connection(port_name, baudrate=9600, timeout=10):
    """Test connection to specified port with enhanced feedback"""
    print(f"\n🔧 Testing connection to {port_name}...")
    print("=" * 50)
    
    try:
        # Open serial connection
        print("📡 Opening serial connection...")
        ser = serial.Serial(port_name, baudrate, timeout=2)
        print(f"✅ Serial port opened successfully")
        print(f"   Port: {port_name}")
        print(f"   Baudrate: {baudrate}")
        print(f"   Timeout: {ser.timeout}s")
        
        # Wait for Arduino reset
        print("⏳ Waiting for Arduino to initialize (3 seconds)...")
        time.sleep(3)
        
        # Clear any buffered data
        ser.flushInput()
        print("🧹 Cleared input buffer")
        
        # Test data reception
        print(f"\n📊 Listening for data (timeout: {timeout}s)...")
        start_time = time.time()
        data_received = False
        valid_data_count = 0
        
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        elapsed = time.time() - start_time
                        print(f"[{elapsed:6.1f}s] 📨 {line}")
                        data_received = True
                        
                        # Check if it's CSV data
                        if ',' in line and not line.startswith('===') and not line.startswith('Time'):
                            parts = line.split(',')
                            if len(parts) >= 3:
                                try:
                                    flow_rate = float(parts[1])
                                    volume = float(parts[2])
                                    status = parts[3] if len(parts) > 3 else "Unknown"
                                    print(f"         📈 Flow: {flow_rate:.3f} L/min | Volume: {volume:.4f} L | Status: {status}")
                                    valid_data_count += 1
                                    
                                    if valid_data_count >= 3:  # Got enough valid data
                                        break
                                except ValueError:
                                    print("         ⚠️  Non-numeric flow data")
                        elif "System ready" in line:
                            print("         🎉 Arduino system is ready!")
                        elif "Connection test" in line:
                            print("         🔍 Arduino running connection test...")
                            
                except UnicodeDecodeError:
                    print(f"[{time.time() - start_time:6.1f}s] ⚠️  Received non-text data")
            
            time.sleep(0.1)
        
        ser.close()
        print("\n" + "=" * 50)
        
        if valid_data_count > 0:
            print(f"🎉 CONNECTION TEST PASSED!")
            print(f"   ✅ Serial communication: Working")
            print(f"   ✅ Arduino code: Uploaded and running")
            print(f"   ✅ Data format: Valid CSV format")
            print(f"   ✅ Data points received: {valid_data_count}")
            print(f"\n🚀 Ready to run: python flow_monitor_gui.py {port_name}")
            return True
        elif data_received:
            print(f"⚠️  CONNECTION TEST PARTIAL")
            print(f"   ✅ Serial communication: Working")
            print(f"   ⚠️  Arduino code: Might need to be uploaded")
            print(f"   ⚠️  Flow sensor: Check connections")
            print(f"\n💡 Try uploading the Arduino code first")
            return False
        else:
            print(f"❌ CONNECTION TEST FAILED")
            print(f"   ✅ Serial communication: Working")
            print(f"   ❌ No data received: Check Arduino code upload")
            print(f"   ❌ Possible issues:")
            print(f"      - Arduino code not uploaded")
            print(f"      - Wrong baud rate")
            print(f"      - Arduino not responding")
            return False
        
    except serial.SerialException as e:
        print(f"❌ SERIAL CONNECTION FAILED")
        print(f"   Error: {e}")
        print(f"   Possible solutions:")
        print(f"   - Check USB cable connection")
        print(f"   - Try a different USB port")
        print(f"   - Close Arduino IDE Serial Monitor")
        print(f"   - Check port permissions")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        if 'ser' in locals():
            ser.close()
        return False

def main():
    print("🔍 Enhanced Arduino Connection Test")
    print("For Liquid Flow Measurement System")
    print("=" * 50)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        port_name = sys.argv[1]
        print(f"Using specified port: {port_name}")
        success = test_connection(port_name)
    else:
        # Auto-detect and show all available ports
        print("🔍 Scanning for available ports...")
        available_ports = get_available_ports()
        
        if not available_ports:
            print("\n❌ No serial ports found!")
            print("\n🔧 Troubleshooting Steps:")
            print("1. 🔌 Connect Arduino via USB cable")
            print("2. 💾 Install Arduino drivers if needed")
            print("3. 🔄 Try a different USB cable")
            print("4. 🖥️  Check Device Manager (Windows) or System Info (macOS)")
            return
        
        print(f"✅ Found {len(available_ports)} port(s)")
        
        # Interactive port selection
        selected_port = select_port_interactive(available_ports)
        
        if not selected_port:
            print("❌ No port selected. Exiting.")
            return
        
        # Test the selected port
        success = test_connection(selected_port)
    
    # Final summary
    print("\n" + "=" * 50)
    if success:
        print("🎊 ALL TESTS PASSED! Your Arduino is ready for flow monitoring.")
    else:
        print("⚠️  Some issues detected. Check the troubleshooting suggestions above.")

if __name__ == "__main__":
    main()
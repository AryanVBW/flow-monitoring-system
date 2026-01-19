#!/usr/bin/env python3
"""
Simple Serial Monitor
Monitor raw serial output from Arduino for debugging
"""

import serial
import time
import sys

def monitor_serial(port, baudrate=9600):
    """Monitor raw serial output"""
    try:
        print(f"🔗 Connecting to {port} at {baudrate} baud...")
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Allow Arduino to reset
        
        print("📡 Monitoring serial output (Press Ctrl+C to stop)...")
        print("=" * 60)
        
        line_count = 0
        start_time = time.time()
        
        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        elapsed = time.time() - start_time
                        line_count += 1
                        print(f"[{elapsed:6.1f}s] #{line_count:03d}: {line}")
                        
                        # Parse CSV data if available
                        if ',' in line and not line.startswith(('===', 'CSV', 'System', 'Starting')):
                            parts = line.split(',')
                            if len(parts) >= 4:
                                try:
                                    timestamp = float(parts[0])
                                    flow_rate = float(parts[1])
                                    volume = float(parts[2])
                                    status = parts[3]
                                    pulses = parts[4] if len(parts) > 4 else "N/A"
                                    total_pulses = parts[5] if len(parts) > 5 else "N/A"
                                    
                                    print(f"         💧 Flow: {flow_rate:.4f} L/min | Volume: {volume:.5f} L")
                                    print(f"         📊 Status: {status} | Pulses: {pulses} | Total: {total_pulses}")
                                except ValueError:
                                    pass
                                    
                except UnicodeDecodeError:
                    print("         ⚠️  Unicode decode error")
                    
            time.sleep(0.01)
            
    except serial.SerialException as e:
        print(f"❌ Serial error: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("🔌 Serial port closed")

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/cu.usbserial-110"
    monitor_serial(port)
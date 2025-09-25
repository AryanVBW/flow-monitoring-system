#!/usr/bin/env python3
"""
Minimal Flow Monitor Test - Check if data is being received and plotted
"""

import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from collections import deque
import threading

# Configuration
PORT = '/dev/cu.usbserial-110'
BAUD_RATE = 9600
MAX_POINTS = 100

class MinimalFlowMonitor:
    def __init__(self):
        self.timestamps = deque(maxlen=MAX_POINTS)
        self.flow_rates = deque(maxlen=MAX_POINTS)
        self.total_volumes = deque(maxlen=MAX_POINTS)
        self.serial_connection = None
        self.running = True
        self.data_count = 0
        
        # Setup plot
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        self.ax1.set_title('Flow Rate (L/min)')
        self.ax2.set_title('Total Volume (L)')
        
        self.line1, = self.ax1.plot([], [], 'b-', linewidth=2)
        self.line2, = self.ax2.plot([], [], 'r-', linewidth=2)
        
        # Start serial reading thread
        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.daemon = True
        
    def connect_arduino(self):
        """Connect to Arduino"""
        try:
            self.serial_connection = serial.Serial(PORT, BAUD_RATE, timeout=2)
            print(f"✅ Connected to Arduino on {PORT}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    def read_serial_data(self):
        """Read data from Arduino in separate thread"""
        if not self.serial_connection:
            return
            
        print("📡 Starting data collection...")
        
        while self.running:
            try:
                line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                if line and "," in line and not line.startswith(("===", "Time", "CSV", "Arduino", "Initializing", "System", "Starting", "---")):
                    self.parse_data_line(line)
                    
            except Exception as e:
                print(f"❌ Serial read error: {e}")
                break
                
            time.sleep(0.01)
    
    def parse_data_line(self, line):
        """Parse CSV data line"""
        try:
            parts = line.split(",")
            if len(parts) < 4:
                return
                
            timestamp_ms = float(parts[0])
            flow_rate = float(parts[1])
            total_volume = float(parts[2])
            status = parts[3].strip()
            
            # Convert timestamp to seconds
            timestamp = timestamp_ms / 1000.0
            
            # Add to data
            self.timestamps.append(timestamp)
            self.flow_rates.append(flow_rate)
            self.total_volumes.append(total_volume)
            
            self.data_count += 1
            
            # Print every 10th data point
            if self.data_count % 10 == 0:
                print(f"📊 Data #{self.data_count}: {flow_rate:.4f} L/min, {total_volume:.5f} L, {status}")
                
        except Exception as e:
            print(f"❌ Parse error for '{line}': {e}")
    
    def animate(self, frame):
        """Update plots"""
        if not self.timestamps:
            return self.line1, self.line2
            
        times = list(self.timestamps)
        flows = list(self.flow_rates)
        volumes = list(self.total_volumes)
        
        # Normalize timestamps to start from 0
        if times:
            start_time = times[0]
            normalized_times = [t - start_time for t in times]
        else:
            normalized_times = []
        
        # Update plots
        self.line1.set_data(normalized_times, flows)
        self.line2.set_data(normalized_times, volumes)
        
        # Auto-scale
        for ax, data in [(self.ax1, flows), (self.ax2, volumes)]:
            if normalized_times and data:
                ax.relim()
                ax.autoscale_view()
                
                # Set reasonable limits
                if max(data) > 0:
                    ax.set_ylim(bottom=0, top=max(data) * 1.1)
                    
                if len(normalized_times) > 1:
                    ax.set_xlim(min(normalized_times), max(normalized_times))
        
        return self.line1, self.line2
    
    def start(self):
        """Start the monitor"""
        if not self.connect_arduino():
            return
            
        # Start serial thread
        self.serial_thread.start()
        
        # Start animation
        ani = animation.FuncAnimation(self.fig, self.animate, interval=100, blit=False)
        
        print("🚀 Monitor started! Close the plot window to exit.")
        plt.tight_layout()
        plt.show()
        
        # Cleanup
        self.running = False
        if self.serial_connection:
            self.serial_connection.close()

if __name__ == "__main__":
    print("🧪 Minimal Flow Monitor Test")
    print("=" * 40)
    
    monitor = MinimalFlowMonitor()
    monitor.start()
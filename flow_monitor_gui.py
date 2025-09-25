#!/usr/bin/env python3
"""
Real-time Flow Rate Monitor and Grapher
For Arduino Liquid Flow Measurement System

This script reads data from the Arduino via serial communication
and creates real-time graphs of flow rate and total volume.

Requirements:
- pyserial
- matplotlib
- numpy

Install with: pip install pyserial matplotlib numpy

Usage:
python flow_monitor_gui.py [COM_PORT]

If no COM_PORT is specified, the script will try to auto-detect.
"""

import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import numpy as np
import time
import sys
import threading
from collections import deque
import serial.tools.list_ports

class FlowMonitor:
    def __init__(self, port=None, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.is_connected = False
        self.is_recording = True
        
        # Data storage
        self.max_points = 300  # Maximum points to display (5 minutes at 1Hz)
        self.timestamps = deque(maxlen=self.max_points)
        self.flow_rates = deque(maxlen=self.max_points)
        self.total_volumes = deque(maxlen=self.max_points)
        self.status_data = deque(maxlen=self.max_points)
        
        # Initialize data with zeros
        self.timestamps.append(0)
        self.flow_rates.append(0)
        self.total_volumes.append(0)
        self.status_data.append("WAITING")
        
        # Statistics
        self.start_time = time.time()
        self.total_data_points = 0
        self.max_flow_rate = 0
        
        # Setup the plot
        self.setup_plot()
        
        # Try to connect
        if self.connect_to_arduino():
            self.start_data_thread()
        
    def find_arduino_port(self):
        """Auto-detect Arduino port"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Arduino' in port.description or 'CH340' in port.description or 'USB' in port.description:
                return port.device
        
        # If no Arduino found, return the first available port
        if ports:
            print(f"Arduino not auto-detected. Trying first available port: {ports[0].device}")
            return ports[0].device
        
        return None
    
    def connect_to_arduino(self):
        """Establish serial connection with Arduino"""
        if not self.port:
            self.port = self.find_arduino_port()
        
        if not self.port:
            print("No serial ports found. Please connect Arduino and restart.")
            return False
        
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            
            # Clear any initial data
            self.serial_connection.flushInput()
            
            print(f"Connected to Arduino on {self.port}")
            self.is_connected = True
            return True
            
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")
            return False
    
    def setup_plot(self):
        """Initialize the matplotlib plot"""
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        self.fig.suptitle('Real-time Liquid Flow Monitor', fontsize=16, fontweight='bold')
        
        # Flow rate plot
        self.ax1.set_title('Flow Rate (L/min)')
        self.ax1.set_ylabel('Flow Rate (L/min)')
        self.ax1.grid(True, alpha=0.3)
        self.line1, = self.ax1.plot([], [], 'b-', linewidth=2, label='Flow Rate')
        self.ax1.legend()
        
        # Total volume plot
        self.ax2.set_title('Cumulative Volume (L)')
        self.ax2.set_xlabel('Time (seconds)')
        self.ax2.set_ylabel('Volume (L)')
        self.ax2.grid(True, alpha=0.3)
        self.line2, = self.ax2.plot([], [], 'r-', linewidth=2, label='Total Volume')
        self.ax2.legend()
        
        # Add control buttons
        self.setup_buttons()
        
        # Status text
        self.status_text = self.fig.text(0.02, 0.95, 'Status: Connecting...', 
                                       fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.9, bottom=0.15)
    
    def setup_buttons(self):
        """Setup control buttons"""
        # Reset button
        ax_reset = plt.axes([0.02, 0.02, 0.1, 0.05])
        self.btn_reset = Button(ax_reset, 'Reset')
        self.btn_reset.on_clicked(self.reset_data)
        
        # Pause/Resume button
        ax_pause = plt.axes([0.13, 0.02, 0.1, 0.05])
        self.btn_pause = Button(ax_pause, 'Pause')
        self.btn_pause.on_clicked(self.toggle_recording)
        
        # Save data button
        ax_save = plt.axes([0.24, 0.02, 0.1, 0.05])
        self.btn_save = Button(ax_save, 'Save Data')
        self.btn_save.on_clicked(self.save_data)
        
        # Stats display
        self.stats_text = self.fig.text(0.4, 0.02, 'Stats: No data', fontsize=9)
    
    def read_serial_data(self):
        """Read data from Arduino in a separate thread"""
        while self.is_connected:
            try:
                if self.serial_connection and self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    
                    # Skip header lines and empty lines
                    if line and ',' in line and not line.startswith('===') and not line.startswith('Time'):
                        self.parse_data_line(line)
                        
            except serial.SerialException:
                print("Serial connection lost")
                self.is_connected = False
                break
            except Exception as e:
                print(f"Error reading serial data: {e}")
            
            time.sleep(0.01)  # Small delay to prevent CPU overload
    
    def parse_data_line(self, line):
        """Parse CSV data line from Arduino"""
        try:
            parts = line.split(',')
            if len(parts) >= 4:
                timestamp = float(parts[0]) / 1000.0  # Convert ms to seconds
                flow_rate = float(parts[1])
                total_volume = float(parts[2])
                status = parts[3].strip()
                
                if self.is_recording:
                    self.timestamps.append(timestamp)
                    self.flow_rates.append(flow_rate)
                    self.total_volumes.append(total_volume)
                    self.status_data.append(status)
                    
                    # Update statistics
                    self.total_data_points += 1
                    if flow_rate > self.max_flow_rate:
                        self.max_flow_rate = flow_rate
                
        except (ValueError, IndexError):
            # Skip malformed lines
            pass
    
    def start_data_thread(self):
        """Start the data reading thread"""
        self.data_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.data_thread.start()
    
    def animate(self, frame):
        """Animation function for matplotlib"""
        if not self.timestamps:
            return self.line1, self.line2
        
        # Convert deques to lists for plotting
        times = list(self.timestamps)
        flows = list(self.flow_rates)
        volumes = list(self.total_volumes)
        
        # Normalize timestamps to start from 0
        if times:
            start_time = times[0]
            times = [t - start_time for t in times]
        
        # Update plots
        self.line1.set_data(times, flows)
        self.line2.set_data(times, volumes)
        
        # Auto-scale axes
        if times and flows:
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.ax2.relim()
            self.ax2.autoscale_view()
        
        # Update status
        current_status = self.status_data[-1] if self.status_data else "NO DATA"
        connection_status = "Connected" if self.is_connected else "Disconnected"
        self.status_text.set_text(f'Status: {connection_status} | Sensor: {current_status}')
        
        # Update statistics
        current_flow = flows[-1] if flows else 0
        current_volume = volumes[-1] if volumes else 0
        runtime = time.time() - self.start_time
        
        stats_text = f'Runtime: {runtime:.0f}s | Points: {self.total_data_points} | '
        stats_text += f'Current Flow: {current_flow:.3f} L/min | '
        stats_text += f'Max Flow: {self.max_flow_rate:.3f} L/min | '
        stats_text += f'Total Volume: {current_volume:.4f} L'
        
        self.stats_text.set_text(stats_text)
        
        return self.line1, self.line2
    
    def reset_data(self, event):
        """Reset all data"""
        self.timestamps.clear()
        self.flow_rates.clear()
        self.total_volumes.clear()
        self.status_data.clear()
        
        # Reset with initial zeros
        self.timestamps.append(0)
        self.flow_rates.append(0)
        self.total_volumes.append(0)
        self.status_data.append("RESET")
        
        self.total_data_points = 0
        self.max_flow_rate = 0
        self.start_time = time.time()
        
        print("Data reset")
    
    def toggle_recording(self, event):
        """Toggle data recording"""
        self.is_recording = not self.is_recording
        self.btn_pause.label.set_text('Resume' if not self.is_recording else 'Pause')
        print(f"Recording {'paused' if not self.is_recording else 'resumed'}")
    
    def save_data(self, event):
        """Save data to CSV file"""
        if not self.timestamps:
            print("No data to save")
            return
        
        filename = f"flow_data_{int(time.time())}.csv"
        try:
            with open(filename, 'w') as f:
                f.write("Time(s),FlowRate(L/min),TotalVolume(L),Status\n")
                
                times = list(self.timestamps)
                flows = list(self.flow_rates)
                volumes = list(self.total_volumes)
                statuses = list(self.status_data)
                
                start_time = times[0] if times else 0
                
                for i in range(len(times)):
                    normalized_time = times[i] - start_time
                    f.write(f"{normalized_time:.3f},{flows[i]:.3f},{volumes[i]:.4f},{statuses[i]}\n")
            
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def run(self):
        """Start the monitoring application"""
        if not self.is_connected:
            print("Cannot start monitoring - no Arduino connection")
            return
        
        # Start animation
        animation.FuncAnimation(self.fig, self.animate, interval=100, blit=False)
        
        print("Flow monitor started. Close the plot window to exit.")
        print("Controls:")
        print("- Reset: Clear all data")
        print("- Pause/Resume: Stop/start data recording")
        print("- Save Data: Export data to CSV file")
        
        plt.show()
        
        # Cleanup
        if self.serial_connection:
            self.serial_connection.close()

def main():
    """Main function"""
    port = None
    
    # Check command line arguments
    if len(sys.argv) > 1:
        port = sys.argv[1]
        print(f"Using specified port: {port}")
    
    # Create and run the monitor
    monitor = FlowMonitor(port=port)
    monitor.run()

if __name__ == "__main__":
    main()
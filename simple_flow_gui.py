#!/usr/bin/env python3
"""
Simple, Working Flow Monitor GUI
Based on the successful minimal test, now with a clean GUI
"""

import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from collections import deque
import threading
import tkinter as tk
from tkinter import messagebox
import seaborn as sns

# Set beautiful seaborn style
sns.set_style("whitegrid")
sns.set_palette("husl")

# Configuration
PORT = '/dev/cu.usbserial-110'
BAUD_RATE = 9600
MAX_POINTS = 500

class SimpleFlowMonitor:
    def __init__(self):
        self.timestamps = deque(maxlen=MAX_POINTS)
        self.flow_rates = deque(maxlen=MAX_POINTS)
        self.total_volumes = deque(maxlen=MAX_POINTS)
        self.serial_connection = None
        self.running = True
        self.data_count = 0
        self.start_time = None
        
        # Setup beautiful plot with seaborn styling
        plt.style.use('seaborn-v0_8')
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Beautiful styling
        self.fig.suptitle('🌊 Liquid Flow Monitoring System', fontsize=16, fontweight='bold', y=0.95)
        
        # Flow rate plot
        self.ax1.set_title('📊 Real-time Flow Rate', fontsize=14, pad=15)
        self.ax1.set_ylabel('Flow Rate (L/min)', fontsize=12)
        self.ax1.grid(True, alpha=0.3)
        
        # Volume plot  
        self.ax2.set_title('📈 Cumulative Volume', fontsize=14, pad=15)
        self.ax2.set_xlabel('Time (seconds)', fontsize=12)
        self.ax2.set_ylabel('Total Volume (L)', fontsize=12)
        self.ax2.grid(True, alpha=0.3)
        
        # Beautiful line plots
        self.line1, = self.ax1.plot([], [], color='#2E86AB', linewidth=2.5, label='Flow Rate', alpha=0.8)
        self.line2, = self.ax2.plot([], [], color='#A23B72', linewidth=2.5, label='Total Volume', alpha=0.8)
        
        # Add legends
        self.ax1.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
        self.ax2.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
        
        # Status display
        self.status_text = self.fig.text(0.02, 0.02, "Status: Connecting...", fontsize=11, 
                                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
        
        # Start serial reading thread
        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.daemon = True
        
    def connect_arduino(self):
        """Connect to Arduino"""
        try:
            self.serial_connection = serial.Serial(PORT, BAUD_RATE, timeout=2)
            print(f"✅ Connected to Arduino on {PORT}")
            self.status_text.set_text("Status: ✅ Connected to Arduino - Collecting data...")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            self.status_text.set_text(f"Status: ❌ Connection failed: {e}")
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
            
            # Get current pulses if available
            current_pulses = int(parts[4]) if len(parts) > 4 else 0
            total_pulses = int(parts[5]) if len(parts) > 5 else 0
            
            # Convert timestamp to seconds from start
            timestamp = timestamp_ms / 1000.0
            if self.start_time is None:
                self.start_time = timestamp
            normalized_time = timestamp - self.start_time
            
            # Add to data
            self.timestamps.append(normalized_time)
            self.flow_rates.append(flow_rate)
            self.total_volumes.append(total_volume)
            
            self.data_count += 1
            
            # Print interesting events
            if current_pulses > 0:
                print(f"🌊 Flow detected: {flow_rate:.3f} L/min ({current_pulses} pulses)")
            elif self.data_count % 50 == 0:  # Every 50th point when no flow
                print(f"📊 Data point #{self.data_count}: {status} - {len(self.timestamps)} points stored")
                
        except Exception as e:
            print(f"❌ Parse error for '{line}': {e}")
    
    def animate(self, frame):
        """Update plots with beautiful animations"""
        if not self.timestamps:
            return self.line1, self.line2
            
        times = list(self.timestamps)
        flows = list(self.flow_rates)
        volumes = list(self.total_volumes)
        
        # Update plots
        self.line1.set_data(times, flows)
        self.line2.set_data(times, volumes)
        
        # Smart auto-scaling with beautiful ranges
        for ax, data, label in [(self.ax1, flows, "L/min"), (self.ax2, volumes, "L")]:
            if times and data:
                ax.relim()
                ax.autoscale_view()
                
                # Set nice limits with padding
                if max(data) > 0:
                    ax.set_ylim(bottom=0, top=max(data) * 1.1)
                else:
                    ax.set_ylim(bottom=0, top=1)
                    
                if len(times) > 1:
                    time_range = max(times) - min(times)
                    padding = max(1, time_range * 0.02)
                    ax.set_xlim(min(times) - padding, max(times) + padding)
        
        # Update status
        current_flow = flows[-1] if flows else 0
        current_volume = volumes[-1] if volumes else 0
        status_msg = f"🌊 Flow: {current_flow:.3f} L/min | 💧 Volume: {current_volume:.3f} L | 📊 Points: {len(times)}"
        
        if current_flow > 0.1:
            status_msg += " | 🟢 FLOW DETECTED!"
        else:
            status_msg += " | 🔵 Waiting for flow..."
            
        self.status_text.set_text(status_msg)
        
        return self.line1, self.line2
    
    def start(self):
        """Start the monitor"""
        if not self.connect_arduino():
            messagebox.showerror("Connection Error", "Failed to connect to Arduino")
            return
            
        # Start serial thread
        self.serial_thread.start()
        
        # Start animation
        ani = animation.FuncAnimation(self.fig, self.animate, interval=100, blit=False, cache_frame_data=False)
        
        print("🚀 Flow Monitor started! Close the plot window to exit.")
        
        # Make plot window responsive
        plt.tight_layout()
        plt.subplots_adjust(top=0.92, bottom=0.08)
        
        # Show plot
        try:
            plt.show()
        except KeyboardInterrupt:
            print("\\n🛑 Interrupted by user")
        
        # Cleanup
        self.running = False
        if self.serial_connection:
            self.serial_connection.close()
        print("✅ Flow Monitor stopped")

if __name__ == "__main__":
    print("🌊 Simple Flow Monitor")
    print("=" * 50)
    print("Features:")
    print("• Real-time flow rate monitoring")
    print("• Beautiful seaborn-styled graphs")
    print("• Automatic liquid flow detection")
    print("• Live status updates")
    print("=" * 50)
    
    monitor = SimpleFlowMonitor()
    monitor.start()
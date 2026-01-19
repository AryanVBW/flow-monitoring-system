#!/usr/bin/env python3
"""
Production-Ready Liquid Flow Monitor GUI
A professional real-time flow monitoring application for Arduino-based flow sensors.

Features:
- Real-time flow rate and volume visualization
- Robust connection management with auto-reconnect
- Data logging and export capabilities
- Professional UI with status indicators
- Production-grade error handling
"""

import sys
import time
import threading
import os
import platform
import logging
from collections import deque
from dataclasses import dataclass
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import messagebox, filedialog

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_SENSOR_STATUS = "NO DATA"
DATA_TIMEOUT_SECONDS = 5.0
RECONNECT_AFTER_SECONDS = 15.0
MAX_POINTS = 500
BAUD_RATE = 9600
PLOT_REFRESH_MS = 100

# Data validation thresholds
FLOW_MAX_REASONABLE = 50.0  # L/min (conservative for SEN-HZ21WA)
FLOW_MIN_REASONABLE = 0.0


@dataclass
class PortInfo:
    """Serial port information container"""
    device: str
    description: str
    type: str
    hwid: str


class PortSelector:
    """Professional port selection dialog with enhanced features"""

    def __init__(self):
        self.selected_port: Optional[str] = None
        self.root: Optional[tk.Tk] = None
        self.port_listbox: Optional[tk.Listbox] = None
        self.status_label: Optional[tk.Label] = None
        self.port_data: List[PortInfo] = []

    def get_available_ports(self) -> List[PortInfo]:
        """Scan and categorize available serial ports"""
        ports = []
        try:
            for port in serial.tools.list_ports.comports():
                descriptor = port.description.upper()
                if any(keyword in descriptor for keyword in ["ARDUINO", "UNO", "NANO", "MEGA"]):
                    port_type = "Arduino"
                elif any(keyword in descriptor for keyword in ["CH340", "CH341", "FTDI", "CP210"]):
                    port_type = "USB-Serial"
                elif "USB" in descriptor:
                    port_type = "USB Device"
                else:
                    port_type = "Unknown"
                
                ports.append(PortInfo(
                    device=port.device,
                    description=port.description,
                    type=port_type,
                    hwid=getattr(port, "hwid", "N/A")
                ))
        except Exception as e:
            logger.error(f"Error scanning ports: {e}")
        
        return sorted(ports, key=lambda x: (x.type != "Arduino", x.device))

    def show_port_selection_dialog(self) -> Optional[str]:
        """Display professional port selection dialog"""
        ports = self.get_available_ports()
        if not ports:
            messagebox.showerror(
                "No Serial Ports Found",
                "No serial ports detected.\n\n"
                "Please ensure your Arduino is connected and drivers are installed."
            )
            return None

        self.root = tk.Tk()
        self.root.title("Flow Monitor - Select Port")
        self.root.geometry("700x450")
        self.root.resizable(True, True)

        # Main container
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Header
        header = tk.Label(main_frame, text="Select Arduino Port", 
                         font=("Arial", 16, "bold"), fg="#2E3440")
        header.pack(pady=(0, 10))

        subtitle = tk.Label(main_frame, text="Choose the port connected to your flow sensor Arduino:",
                           font=("Arial", 10), fg="#5E81AC")
        subtitle.pack(pady=(0, 15))

        # Port list with scrollbar
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=(0, 15))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.port_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            height=12,
            selectmode=tk.SINGLE
        )
        self.port_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.port_listbox.yview)

        # Populate port list
        self.port_data = ports
        for i, port in enumerate(ports):
            if port.type == "Arduino":
                icon = "�"
            elif port.type == "USB-Serial":
                icon = "📱"
            else:
                icon = "🔗"
            display = f"{icon} {port.device:<20} │ {port.type:<12} │ {port.description}"
            self.port_listbox.insert(tk.END, display)
            
            # Auto-select Arduino ports
            if port.type == "Arduino":
                self.port_listbox.selection_set(i)
                self.port_listbox.see(i)

        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(15, 0))

        # Control buttons
        tk.Button(button_frame, text="🔄 Refresh", command=self.refresh_ports,
                 font=("Arial", 10), padx=15).pack(side="left")
        
        tk.Button(button_frame, text="🔍 Test Port", command=self.test_selected_port,
                 font=("Arial", 10), padx=15).pack(side="left", padx=(10, 0))

        tk.Button(button_frame, text="❌ Cancel", command=self.cancel_selection,
                 font=("Arial", 10), padx=15).pack(side="right")
        
        tk.Button(button_frame, text="✅ Connect", command=self.confirm_selection,
                 font=("Arial", 10), bg="#A3BE8C", fg="white", padx=20).pack(side="right", padx=(0, 10))

        # Status bar
        self.status_label = tk.Label(main_frame, text="Select a port and click Connect",
                                   font=("Arial", 9), fg="#5E81AC")
        self.status_label.pack(pady=(15, 0))

        # Center window
        self.root.update_idletasks()
        self._center_window()
        
        self.root.mainloop()
        return self.selected_port

    def _center_window(self):
        """Center the dialog window on screen"""
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def refresh_ports(self):
        """Refresh the port list"""
        if not self.port_listbox or not self.status_label:
            return
            
        self.status_label.config(text="Refreshing ports...", fg="orange")
        self.port_listbox.delete(0, tk.END)
        self.port_data = self.get_available_ports()
        
        for i, port in enumerate(self.port_data):
            if port.type == "Arduino":
                icon = "�"
            elif port.type == "USB-Serial":
                icon = "📱"
            else:
                icon = "🔗"
            display = f"{icon} {port.device:<20} │ {port.type:<12} │ {port.description}"
            self.port_listbox.insert(tk.END, display)
            
        self.status_label.config(text=f"Found {len(self.port_data)} port(s)", fg="#5E81AC")

    def test_selected_port(self):
        """Test connection to selected port"""
        if not self.port_listbox or not self.status_label:
            return
            
        selection = self.port_listbox.curselection()
        if not selection:
            self.status_label.config(text="Please select a port first!", fg="red")
            return

        port = self.port_data[selection[0]]
        self.status_label.config(text=f"Testing {port.device}...", fg="orange")
        self.root.update()

        try:
            with serial.Serial(port.device, BAUD_RATE, timeout=2) as test_connection:
                time.sleep(1)
                test_connection.close()  # Explicitly close the test connection
                self.status_label.config(text=f"✅ {port.device} connection successful", fg="green")
        except Exception as e:
            self.status_label.config(text=f"❌ Test failed: {str(e)[:50]}...", fg="red")

    def confirm_selection(self):
        """Confirm port selection"""
        if not self.port_listbox:
            return
            
        selection = self.port_listbox.curselection()
        if not selection:
            if self.status_label:
                self.status_label.config(text="Please select a port first!", fg="red")
            return

        self.selected_port = self.port_data[selection[0]].device
        if self.root:
            self.root.quit()
            self.root.destroy()

    def cancel_selection(self):
        """Cancel port selection"""
        self.selected_port = None
        if self.root:
            self.root.quit()
            self.root.destroy()


class FlowMonitor:
    """Production-grade flow monitoring system"""

    def __init__(self, port: Optional[str], baudrate: int = BAUD_RATE):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_recording = True
        self.is_running = True

        # Data storage with thread-safe collections
        self.timestamps = deque(maxlen=MAX_POINTS)
        self.flow_rates = deque(maxlen=MAX_POINTS)
        self.total_volumes = deque(maxlen=MAX_POINTS)
        self.status_history = deque(maxlen=MAX_POINTS)

        # Initialize with zero values
        self._reset_data_internal()

        # Statistics and state
        self.start_time = time.time()
        self.total_data_points = 0
        self.max_flow_rate = 0.0
        self.last_data_timestamp: Optional[float] = None
        self.last_reconnect_attempt: Optional[float] = None
        self.sensor_status = DEFAULT_SENSOR_STATUS
        self.latest_flow_rate = 0.0
        self.latest_total_volume = 0.0

        # GUI components
        self.fig = None
        self.ax1 = None
        self.ax2 = None
        self.line1 = None
        self.line2 = None
        self.status_text = None
        self.stats_text = None
        self.btn_pause = None

        # Thread management
        self.data_thread: Optional[threading.Thread] = None
        self.thread_lock = threading.Lock()

        self._setup_plot()
        if self._connect_to_arduino():
            self._start_data_thread()

    def _reset_data_internal(self):
        """Internal data reset without GUI updates"""
        self.timestamps.clear()
        self.flow_rates.clear()
        self.total_volumes.clear()
        self.status_history.clear()

        self.timestamps.append(0.0)
        self.flow_rates.append(0.0)
        self.total_volumes.append(0.0)
        self.status_history.append(DEFAULT_SENSOR_STATUS)

    def _normalize_port_device(self, device: str) -> str:
        """Normalize port device name for better compatibility"""
        try:
            if platform.system() == "Darwin" and device.startswith("/dev/cu."):
                tty_variant = device.replace("/dev/cu.", "/dev/tty.", 1)
                if os.path.exists(tty_variant):
                    logger.info(f"Using {tty_variant} instead of {device} for better stability")
                    return tty_variant
        except Exception:
            pass
        return device

    def _find_arduino_port(self) -> Optional[str]:
        """Auto-detect Arduino port"""
        try:
            for port in serial.tools.list_ports.comports():
                descriptor = port.description.upper()
                if any(keyword in descriptor for keyword in ["ARDUINO", "CH340", "CH341", "USB"]):
                    return port.device
            
            # Fallback to first available port
            ports = list(serial.tools.list_ports.comports())
            return ports[0].device if ports else None
        except Exception as e:
            logger.error(f"Error finding Arduino port: {e}")
            return None

    def _connect_to_arduino(self) -> bool:
        """Establish serial connection with Arduino"""
        if not self.port:
            self.port = self._find_arduino_port()
        
        if not self.port:
            logger.error("No serial ports available")
            return False

        try:
            normalized_port = self._normalize_port_device(self.port)
            self.serial_connection = serial.Serial(normalized_port, self.baudrate, timeout=1)
            time.sleep(2)  # Allow Arduino to reset
            self.serial_connection.flushInput()
            
            self.is_connected = True
            self.last_data_timestamp = None
            self.sensor_status = DEFAULT_SENSOR_STATUS
            
            logger.info(f"Connected to Arduino on {normalized_port}")
            return True
            
        except serial.SerialException as e:
            logger.error(f"Failed to connect to {self.port}: {e}")
            self.is_connected = False
            return False

    def _setup_plot(self):
        """Initialize a beautiful, modern plotting interface"""
        # Use a clean, modern style
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Create figure with beautiful proportions
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(16, 10), 
                                                     facecolor='white', edgecolor='none')
        
        # Modern title with clean design
        self.fig.suptitle("Liquid Flow Monitor", fontsize=24, fontweight='300', 
                         color="#1a1a1a", y=0.96)
        
        # Beautiful color palette
        primary_color = "#0066cc"      # Beautiful blue
        secondary_color = "#ff6b35"    # Vibrant orange
        grid_color = "#f0f0f0"         # Very light gray
        bg_color = "#fafafa"           # Off-white background
        
        # Flow Rate Plot - Top panel
        self.ax1.set_facecolor(bg_color)
        self.ax1.set_title("Flow Rate", fontsize=16, fontweight='400', 
                          color="#333333", pad=20)
        self.ax1.set_ylabel("Liters per Minute", fontsize=12, color="#666666")
        
        # Beautiful grid
        self.ax1.grid(True, linestyle='-', alpha=0.3, color=grid_color, linewidth=0.8)
        self.ax1.set_axisbelow(True)
        
        # Smooth, thick line for flow rate
        self.line1, = self.ax1.plot([], [], color=primary_color, linewidth=3.5, 
                                   label="Flow Rate", alpha=0.9, 
                                   marker='o', markersize=0, markevery=10)
        
        # Beautiful legend
        legend1 = self.ax1.legend(loc="upper right", frameon=True, fancybox=True, 
                                 shadow=True, framealpha=0.9, fontsize=11)
        legend1.get_frame().set_facecolor('white')
        legend1.get_frame().set_edgecolor('#cccccc')
        
        # Volume Plot - Bottom panel  
        self.ax2.set_facecolor(bg_color)
        self.ax2.set_title("Cumulative Volume", fontsize=16, fontweight='400', 
                          color="#333333", pad=20)
        self.ax2.set_xlabel("Time (seconds)", fontsize=12, color="#666666")
        self.ax2.set_ylabel("Total Liters", fontsize=12, color="#666666")
        
        # Beautiful grid
        self.ax2.grid(True, linestyle='-', alpha=0.3, color=grid_color, linewidth=0.8)
        self.ax2.set_axisbelow(True)
        
        # Smooth, thick line for volume
        self.line2, = self.ax2.plot([], [], color=secondary_color, linewidth=3.5, 
                                   label="Total Volume", alpha=0.9,
                                   marker='o', markersize=0, markevery=10)
        
        # Beautiful legend
        legend2 = self.ax2.legend(loc="upper left", frameon=True, fancybox=True, 
                                 shadow=True, framealpha=0.9, fontsize=11)
        legend2.get_frame().set_facecolor('white')
        legend2.get_frame().set_edgecolor('#cccccc')
        
        # Style the axes
        for ax in [self.ax1, self.ax2]:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#cccccc')
            ax.spines['bottom'].set_color('#cccccc')
            ax.tick_params(colors='#666666', labelsize=10)
        
        self._setup_controls()
        
        # Modern status displays
        self.status_text = self.fig.text(0.02, 0.94, "Status: Initializing system...", 
                                       fontsize=12, fontweight='500', color="#333333")
        self.stats_text = self.fig.text(0.02, 0.02, "Waiting for data...", 
                                      fontsize=10, color="#777777")

        # Adjust layout for beauty
        plt.tight_layout()
        plt.subplots_adjust(top=0.90, bottom=0.15, left=0.08, right=0.95, hspace=0.35)

    def _setup_controls(self):
        """Setup beautiful, modern control buttons"""
        # Modern button styling
        button_height = 0.05
        button_width = 0.09
        button_y = 0.03
        
        # Reset button - Clean gray
        ax_reset = plt.axes([0.68, button_y, button_width, button_height])
        btn_reset = Button(ax_reset, "Reset", color="#f8f9fa", hovercolor="#e9ecef")
        btn_reset.label.set_color("#495057")
        btn_reset.label.set_fontweight('500')
        btn_reset.on_clicked(self.reset_data)

        # Pause/Resume button - Blue accent
        ax_pause = plt.axes([0.78, button_y, button_width, button_height])
        self.btn_pause = Button(ax_pause, "Pause", color="#0066cc", hovercolor="#0052a3")
        self.btn_pause.label.set_color("white")
        self.btn_pause.label.set_fontweight('500')
        self.btn_pause.on_clicked(self.toggle_recording)

        # Save button - Success green
        ax_save = plt.axes([0.88, button_y, button_width, button_height])
        btn_save = Button(ax_save, "Save", color="#28a745", hovercolor="#218838")
        btn_save.label.set_color("white")
        btn_save.label.set_fontweight('500')
        btn_save.on_clicked(self.save_data)

    def _start_data_thread(self):
        """Start the data reading thread"""
        if self.data_thread and self.data_thread.is_alive():
            return
            
        self.data_thread = threading.Thread(target=self._read_serial_data, daemon=True)
        self.data_thread.start()
        logger.info("Data reading thread started")

    def _read_serial_data(self):
        """Thread function for reading serial data"""
        while self.is_connected and self.is_running:
            try:
                if self.serial_connection and self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode("utf-8", errors="ignore").strip()
                    if line and "," in line and not line.startswith(("===", "Time", "CSV")):
                        self._parse_data_line(line)
                        
            except serial.SerialException as e:
                logger.error(f"Serial connection lost: {e}")
                self.is_connected = False
                break
            except Exception as e:
                logger.error(f"Error reading serial data: {e}")
                
            time.sleep(0.01)

    def _parse_data_line(self, line: str):
        """Parse incoming CSV data line with enhanced debug support"""
        try:
            parts = line.split(",")
            if len(parts) < 4:
                logger.debug(f"Skipping line with insufficient parts: {line}")
                return

            timestamp_ms = float(parts[0])
            flow_rate = float(parts[1])
            total_volume = float(parts[2])
            status = parts[3].strip() or DEFAULT_SENSOR_STATUS
            
            # Extract debug info if available (new format includes pulse counts)
            current_pulses = int(parts[4]) if len(parts) > 4 else 0
            total_pulses = int(parts[5]) if len(parts) > 5 else 0

            # Debug: Log every 10th data point to see if we're receiving data
            if timestamp_ms % 10000 < 1000:  # Log roughly every 10 seconds
                logger.info(f"Data point: {flow_rate:.4f} L/min, {total_volume:.5f} L, {status} ({len(self.timestamps)} points stored)")

            # More lenient validation - allow small flows that were previously rejected
            if flow_rate < 0:
                logger.warning(f"Negative flow rate: {flow_rate} L/min")
                return
            
            # Only warn about unreasonably high flows (above 20 L/min for household use)
            if flow_rate > 20.0:
                logger.warning(f"Very high flow rate: {flow_rate} L/min ({current_pulses} pulses)")
            
            # Log pulse activity for debugging
            if current_pulses > 0:
                logger.info(f"Flow detected: {flow_rate:.4f} L/min ({current_pulses} pulses, total: {total_pulses})")

            timestamp = timestamp_ms / 1000.0
            
            with self.thread_lock:
                self.last_data_timestamp = time.time()
                self.sensor_status = status
                self.latest_flow_rate = flow_rate
                self.latest_total_volume = total_volume

                if self.is_recording:
                    self.timestamps.append(timestamp)
                    self.flow_rates.append(flow_rate)
                    self.total_volumes.append(total_volume)
                    self.status_history.append(status)
                    self.total_data_points += 1
                    self.max_flow_rate = max(self.max_flow_rate, flow_rate)
                    
                    # Debug: Log when we add data points
                    if self.total_data_points % 50 == 0:  # Every 50 points
                        logger.info(f"Added data point #{self.total_data_points}: {flow_rate:.4f} L/min")

        except (ValueError, IndexError) as e:
            logger.debug(f"Failed to parse data line '{line}': {e}")

    def _compute_status_summary(self) -> Tuple[str, str, str, str, float]:
        """Compute current system status"""
        with self.thread_lock:
            connection_status = "Connected" if self.is_connected else "Disconnected"
            now = time.time()
            
            if self.last_data_timestamp is not None:
                delta = now - self.last_data_timestamp
                if delta > DATA_TIMEOUT_SECONDS:
                    data_status = f"Stale ({delta:.1f}s)"
                    sensor_display = f"{self.sensor_status} (stale)"
                else:
                    data_status = "Receiving"
                    sensor_display = self.sensor_status
                last_update = f"{delta:.1f}s ago"
            else:
                data_status = "Waiting..."
                sensor_display = DEFAULT_SENSOR_STATUS
                last_update = "n/a"

            if not self.is_connected:
                data_status = "No connection"
                sensor_display = f"{self.sensor_status} (disconnected)"

            return connection_status, data_status, sensor_display, last_update, now

    def _update_displays(self, connection: str, data: str, sensor: str, 
                        runtime: float, last_update: str):
        """Update beautiful status and statistics displays"""
        # Beautiful status display
        if connection == "Connected" and data == "Receiving":
            status_color = "#28a745"
            status_msg = "Connected & Receiving Data"
        elif "Stale" in data or "Waiting" in data:
            status_color = "#ffc107"
            status_msg = f"Connected - {data}"
        else:
            status_color = "#dc3545"
            status_msg = "Connection Issue"
        
        self.status_text.set_text(f"Status: {status_msg} | Sensor: {sensor}")
        self.status_text.set_color(status_color)

        # Beautiful statistics display with icons and formatting
        with self.thread_lock:
            current_flow = self.latest_flow_rate if self.last_data_timestamp else 0.0
            current_volume = self.latest_total_volume if self.last_data_timestamp else 0.0
        
        # Format runtime nicely
        if runtime < 60:
            runtime_str = f"{runtime:.0f}s"
        elif runtime < 3600:
            runtime_str = f"{runtime/60:.1f}m"
        else:
            runtime_str = f"{runtime/3600:.1f}h"
        
        stats = (f"Runtime: {runtime_str} | "
                f"Data Points: {self.total_data_points:,} | "
                f"Current: {current_flow:.2f} L/min | "
                f"Peak: {self.max_flow_rate:.2f} L/min | "
                f"Total: {current_volume:.3f} L | "
                f"Last Update: {last_update}")
        self.stats_text.set_text(stats)

    def animate(self, frame):
        """Animation function for real-time plotting"""
        if not self.timestamps:
            return self.line1, self.line2

        with self.thread_lock:
            times = list(self.timestamps)
            flows = list(self.flow_rates)
            volumes = list(self.total_volumes)

        # Normalize timestamps
        if times:
            start_time = times[0]
            normalized_times = [t - start_time for t in times]
        else:
            normalized_times = []

        # Update plot data with smooth curves
        self.line1.set_data(normalized_times, flows)
        self.line2.set_data(normalized_times, volumes)

        # Smart auto-scaling with padding for beauty
        if normalized_times and flows:
            # Flow rate plot scaling
            self.ax1.relim()
            self.ax1.autoscale_view()
            if max(flows) > 0:
                self.ax1.set_ylim(bottom=-0.1, top=max(flows) * 1.1)
            
            # Volume plot scaling  
            self.ax2.relim()
            self.ax2.autoscale_view()
            if max(volumes) > 0:
                self.ax2.set_ylim(bottom=-0.01, top=max(volumes) * 1.05)
            
            # Set nice time axis limits
            if len(normalized_times) > 1:
                time_range = max(normalized_times) - min(normalized_times)
                if time_range > 0:
                    padding = time_range * 0.02  # 2% padding
                    self.ax1.set_xlim(min(normalized_times) - padding, 
                                     max(normalized_times) + padding)
                    self.ax2.set_xlim(min(normalized_times) - padding, 
                                     max(normalized_times) + padding)

        # Update displays
        connection, data, sensor, last_update, now = self._compute_status_summary()
        runtime = now - self.start_time
        self._update_displays(connection, data, sensor, runtime, last_update)

        # Auto-reconnect logic
        self._handle_auto_reconnect(now)

        return self.line1, self.line2

    def _handle_auto_reconnect(self, now: float):
        """Handle automatic reconnection attempts"""
        if (self.is_connected and self.last_data_timestamp and 
            now - self.last_data_timestamp > RECONNECT_AFTER_SECONDS):
            
            if not self.last_reconnect_attempt or now - self.last_reconnect_attempt > 5.0:
                self.last_reconnect_attempt = now
                logger.info("Attempting auto-reconnect...")
                
                try:
                    self._close_connection()
                    if self._connect_to_arduino():
                        self._start_data_thread()
                except Exception as e:
                    logger.error(f"Auto-reconnect failed: {e}")

    def _close_connection(self):
        """Safely close serial connection"""
        try:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
        except Exception:
            pass
        finally:
            self.serial_connection = None
            self.is_connected = False

    # GUI Event Handlers
    def reset_data(self, event):
        """Reset all data and statistics"""
        with self.thread_lock:
            self._reset_data_internal()
            self.total_data_points = 0
            self.max_flow_rate = 0.0
            self.start_time = time.time()
            self.last_data_timestamp = None
            self.sensor_status = DEFAULT_SENSOR_STATUS
            self.latest_flow_rate = 0.0
            self.latest_total_volume = 0.0
        
        logger.info("Data reset completed")

    def toggle_recording(self, event):
        """Toggle data recording on/off"""
        self.is_recording = not self.is_recording
        if self.btn_pause:
            if self.is_recording:
                self.btn_pause.label.set_text("Pause")
                self.btn_pause.color = "#0066cc"
                self.btn_pause.hovercolor = "#0052a3"
            else:
                self.btn_pause.label.set_text("Resume")
                self.btn_pause.color = "#28a745"
                self.btn_pause.hovercolor = "#218838"
        
        status = "paused" if not self.is_recording else "resumed"
        logger.info(f"Recording {status}")

    def save_data(self, event):
        """Save current data to CSV file"""
        if len(self.timestamps) <= 1:
            messagebox.showwarning("No Data", "No data to save!")
            return

        # Use file dialog for save location
        filename = filedialog.asksaveasfilename(
            title="Save Flow Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialname=f"flow_data_{int(time.time())}.csv"
        )
        
        if not filename:
            return

        try:
            with self.thread_lock:
                times = list(self.timestamps)
                flows = list(self.flow_rates)
                volumes = list(self.total_volumes)
                statuses = list(self.status_history)

            if times:
                start_time = times[0]
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("Time(s),FlowRate(L/min),TotalVolume(L),Status\n")
                    for i, timestamp in enumerate(times):
                        normalized_time = timestamp - start_time
                        status = statuses[i] if i < len(statuses) else self.sensor_status
                        f.write(f"{normalized_time:.3f},{flows[i]:.3f},{volumes[i]:.4f},{status}\n")
                
                logger.info(f"Data saved to {filename}")
                messagebox.showinfo("Save Successful", f"Data saved to:\n{filename}")
                
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            messagebox.showerror("Save Failed", f"Failed to save data:\n{str(e)}")

    def run(self):
        """Start the monitoring application"""
        if not self.is_connected:
            messagebox.showerror("Connection Error", 
                               "Cannot start monitoring - no serial connection available")
            return

        try:
            logger.info("Starting flow monitor...")
            # Keep animation reference to prevent garbage collection
            self.animation = animation.FuncAnimation(self.fig, self.animate, interval=PLOT_REFRESH_MS, 
                                                   blit=False, cache_frame_data=False)
            
            # Set up window close handler
            def on_close(event):
                self.is_running = False
                self._close_connection()
                plt.close('all')
            
            self.fig.canvas.mpl_connect('close_event', on_close)
            
            plt.show()
            
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        finally:
            self.is_running = False
            self._close_connection()


def select_port_interactively() -> Optional[str]:
    """Interactive port selection with enhanced UI"""
    logger.info("Starting port selection...")
    selector = PortSelector()
    ports = selector.get_available_ports()
    
    if not ports:
        logger.error("No serial ports found")
        return None

    # Auto-select if only one Arduino found
    arduino_ports = [p for p in ports if p.type == "Arduino"]
    if len(arduino_ports) == 1:
        port = arduino_ports[0].device
        logger.info(f"Auto-selected Arduino port: {port}")
        return port

    # Show selection dialog
    return selector.show_port_selection_dialog()


def main():
    """Main application entry point"""
    logger.info("Flow Monitor starting...")
    
    try:
        # Handle command line argument
        port = sys.argv[1] if len(sys.argv) > 1 else None
        
        if not port:
            port = select_port_interactively()
        
        if not port:
            logger.info("No port selected, exiting")
            return

        # Create and run monitor
        logger.info(f"Initializing Flow Monitor on {port}")
        monitor = FlowMonitor(port=port)
        monitor.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        messagebox.showerror("Application Error", f"An error occurred:\n{str(e)}")
    finally:
        logger.info("Flow Monitor shutdown complete")


if __name__ == "__main__":
    main()
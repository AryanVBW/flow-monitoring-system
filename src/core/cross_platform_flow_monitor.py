#!/usr/bin/env python3
"""
Cross-Platform Liquid Flow Monitor GUI
Compatible with Windows x64, macOS, and Linux

Features:
- Cross-platform serial port detection
- Enhanced error handling and recovery
- Windows-specific optimizations
- Beautiful cross-platform GUI
- Automatic port selection
- Robust connection management
"""

import sys
import time
import threading
import os
import platform
import logging
from collections import deque
from typing import List, Optional, Tuple
import traceback

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("❌ Error: pyserial not installed")
    print("Install with: pip install pyserial")
    sys.exit(1)

# Check tkinter FIRST - matplotlib backend depends on it
try:
    import tkinter as tk
    from tkinter import messagebox, ttk, filedialog
except ImportError:
    print("❌ Error: tkinter not available")
    print("")
    if platform.system() == "Linux":
        print("Install with: sudo apt-get install python3-tk")
    elif platform.system() == "Darwin":  # macOS
        print("Install with: brew install python-tk@3.11")
        print("Or reinstall Python with tkinter support")
    else:  # Windows
        print("Reinstall Python from python.org with tcl/tk option enabled")
    sys.exit(1)

# Now import matplotlib (depends on tkinter for TkAgg backend)
try:
    import matplotlib

    matplotlib.use("TkAgg")  # Set backend before importing pyplot
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except ImportError as e:
    print(f"❌ Error: matplotlib not installed or misconfigured")
    print(f"   Details: {e}")
    print("Install with: pip install matplotlib")
    sys.exit(1)

try:
    import seaborn as sns

    sns.set_style("whitegrid")
    HAS_SEABORN = True
except ImportError:
    print("⚠️  Warning: seaborn not installed (optional)")
    print("Install with: pip install seaborn")
    HAS_SEABORN = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("flow_monitor.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)

# Configuration constants
BAUD_RATE = 9600
MAX_POINTS = 500
PLOT_REFRESH_MS = 100
CONNECTION_TIMEOUT = 10.0
RECONNECT_INTERVAL = 5.0


class CrossPlatformFlowMonitor:
    def __init__(self):
        self.system = platform.system()
        logger.info(f"Starting Flow Monitor on {self.system} {platform.machine()}")

        # Data storage
        self.timestamps = deque(maxlen=MAX_POINTS)
        self.flow_rates = deque(maxlen=MAX_POINTS)
        self.total_volumes = deque(maxlen=MAX_POINTS)

        # Connection management
        self.serial_connection: Optional[serial.Serial] = None
        self.selected_port: Optional[str] = None
        self.is_connected = False
        self.is_running = True
        self.data_count = 0
        self.start_time = None

        # Threading
        self.serial_thread: Optional[threading.Thread] = None
        self.thread_lock = threading.Lock()

        # GUI setup
        self.setup_gui()

    def setup_gui(self):
        """Setup cross-platform GUI"""
        self.root = tk.Tk()
        self.root.title("🌊 Liquid Flow Monitor - Cross Platform")
        self.root.geometry("1200x800")

        # Set icon if available
        try:
            if self.system == "Windows":
                self.root.iconbitmap(default="flow_icon.ico")
        except:
            pass

        # Configure for high DPI on Windows
        if self.system == "Windows":
            try:
                from ctypes import windll

                windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass

        self.setup_menu()
        self.setup_toolbar()
        self.setup_plots()
        self.setup_status_bar()

        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Connection menu
        conn_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Connection", menu=conn_menu)
        conn_menu.add_command(label="Select Port", command=self.select_port)
        conn_menu.add_command(label="Reconnect", command=self.reconnect)
        conn_menu.add_separator()
        conn_menu.add_command(label="Refresh Ports", command=self.refresh_ports)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def setup_toolbar(self):
        """Setup toolbar with connection controls"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Port selection
        ttk.Label(toolbar, text="Port:").pack(side=tk.LEFT, padx=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(toolbar, textvariable=self.port_var, width=20)
        self.port_combo.pack(side=tk.LEFT, padx=5)

        # Connection buttons
        self.connect_btn = ttk.Button(
            toolbar, text="Connect", command=self.connect_arduino
        )
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        self.disconnect_btn = ttk.Button(
            toolbar,
            text="Disconnect",
            command=self.disconnect_arduino,
            state=tk.DISABLED,
        )
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)

        # Refresh ports button
        ttk.Button(toolbar, text="Refresh Ports", command=self.refresh_ports).pack(
            side=tk.LEFT, padx=5
        )

        # Status indicator
        self.status_var = tk.StringVar(value="Disconnected")
        self.status_label = ttk.Label(
            toolbar, textvariable=self.status_var, foreground="red"
        )
        self.status_label.pack(side=tk.RIGHT, padx=5)

        # Initial port refresh
        self.refresh_ports()

    def setup_plots(self):
        """Setup matplotlib plots embedded in tkinter"""
        # Create matplotlib figure
        if HAS_SEABORN:
            plt.style.use("seaborn-v0_8")

        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        self.fig.suptitle(
            "🌊 Real-time Liquid Flow Monitoring", fontsize=14, fontweight="bold"
        )

        # Configure plots
        self.ax1.set_title("Flow Rate (L/min)", fontsize=12)
        self.ax1.set_ylabel("Flow Rate (L/min)")
        self.ax1.grid(True, alpha=0.3)

        self.ax2.set_title("Cumulative Volume (L)", fontsize=12)
        self.ax2.set_xlabel("Time (seconds)")
        self.ax2.set_ylabel("Total Volume (L)")
        self.ax2.grid(True, alpha=0.3)

        # Plot lines with initial data point to ensure lines are visible
        (self.line1,) = self.ax1.plot([0], [0], "b-", linewidth=2, label="Flow Rate")
        (self.line2,) = self.ax2.plot([0], [0], "r-", linewidth=2, label="Total Volume")

        # Set initial axis limits so the plot is visible from the start
        self.ax1.set_xlim(0, 10)
        self.ax1.set_ylim(0, 1)
        self.ax2.set_xlim(0, 10)
        self.ax2.set_ylim(0, 0.1)

        self.ax1.legend(loc="upper right")
        self.ax2.legend(loc="upper left")

        # Apply tight layout
        self.fig.tight_layout()

        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Toolbar for matplotlib
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

        toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        toolbar.update()

        # Initial draw to display the empty graph
        self.canvas.draw()

    def setup_status_bar(self):
        """Setup status bar"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.data_status = tk.StringVar(value="No data")
        ttk.Label(self.status_frame, textvariable=self.data_status).pack(
            side=tk.LEFT, padx=5
        )

        self.stats_status = tk.StringVar(value="Ready")
        ttk.Label(self.status_frame, textvariable=self.stats_status).pack(
            side=tk.RIGHT, padx=5
        )

    def get_available_ports(self) -> List[str]:
        """Get list of available serial ports with cross-platform support"""
        ports = []
        try:
            available_ports = serial.tools.list_ports.comports()
            for port in available_ports:
                port_name = port.device
                description = port.description or "Unknown device"

                # Filter for likely Arduino ports
                if any(
                    keyword in description.lower()
                    for keyword in [
                        "arduino",
                        "usb",
                        "serial",
                        "ch340",
                        "cp210",
                        "ftdi",
                    ]
                ):
                    ports.append(f"{port_name} ({description})")
                else:
                    ports.append(f"{port_name} ({description})")

            logger.info(f"Found {len(ports)} serial ports")
        except Exception as e:
            logger.error(f"Error scanning ports: {e}")
            messagebox.showerror("Error", f"Failed to scan serial ports: {e}")

        return ports

    def refresh_ports(self):
        """Refresh available ports in combo box"""
        try:
            ports = self.get_available_ports()
            self.port_combo["values"] = ports

            if ports and not self.port_var.get():
                # Auto-select first Arduino-like port
                for port in ports:
                    if any(keyword in port.lower() for keyword in ["arduino", "usb"]):
                        self.port_combo.set(port)
                        break
                else:
                    self.port_combo.set(ports[0])

        except Exception as e:
            logger.error(f"Error refreshing ports: {e}")

    def select_port(self):
        """Manual port selection dialog"""
        ports = self.get_available_ports()
        if not ports:
            messagebox.showwarning("No Ports", "No serial ports found")
            return

        # Simple selection for now, could enhance with custom dialog
        self.refresh_ports()

    def extract_port_name(self, port_string: str) -> str:
        """Extract actual port name from display string"""
        if "(" in port_string:
            return port_string.split("(")[0].strip()
        return port_string.strip()

    def connect_arduino(self):
        """Connect to Arduino with enhanced error handling"""
        if self.is_connected:
            return

        port_string = self.port_var.get()
        if not port_string:
            messagebox.showwarning("No Port", "Please select a serial port")
            return

        self.selected_port = self.extract_port_name(port_string)

        try:
            logger.info(f"Attempting to connect to {self.selected_port}")

            # Windows-specific port handling
            if self.system == "Windows" and not self.selected_port.startswith("COM"):
                if "COM" in self.selected_port.upper():
                    # Extract COM port number
                    import re

                    com_match = re.search(r"COM(\d+)", self.selected_port.upper())
                    if com_match:
                        self.selected_port = f"COM{com_match.group(1)}"

            # Attempt connection with timeout
            self.serial_connection = serial.Serial(
                port=self.selected_port,
                baudrate=BAUD_RATE,
                timeout=2,
                write_timeout=2,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )

            # Test connection
            time.sleep(1)  # Wait for Arduino to initialize

            self.is_connected = True
            self.status_var.set("Connected")
            self.status_label.configure(foreground="green")
            self.connect_btn.configure(state=tk.DISABLED)
            self.disconnect_btn.configure(state=tk.NORMAL)

            # Start data reading thread
            self.start_data_thread()

            # Start animation
            self.start_animation()

            logger.info(f"Successfully connected to {self.selected_port}")

        except serial.SerialException as e:
            error_msg = f"Serial connection failed: {e}"
            logger.error(error_msg)
            messagebox.showerror("Connection Error", error_msg)
            self.cleanup_connection()

        except Exception as e:
            error_msg = f"Unexpected connection error: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            messagebox.showerror("Connection Error", error_msg)
            self.cleanup_connection()

    def disconnect_arduino(self):
        """Disconnect from Arduino"""
        try:
            self.is_running = False

            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()

            self.cleanup_connection()
            logger.info("Disconnected from Arduino")

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    def cleanup_connection(self):
        """Clean up connection state"""
        self.is_connected = False
        self.status_var.set("Disconnected")
        self.status_label.configure(foreground="red")
        self.connect_btn.configure(state=tk.NORMAL)
        self.disconnect_btn.configure(state=tk.DISABLED)

        if self.serial_connection:
            try:
                self.serial_connection.close()
            except:
                pass
            self.serial_connection = None

    def start_data_thread(self):
        """Start serial data reading thread"""
        if self.serial_thread and self.serial_thread.is_alive():
            return

        self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.serial_thread.start()

    def read_serial_data(self):
        """Read data from Arduino with error recovery"""
        logger.info("Started data reading thread")

        consecutive_errors = 0
        max_consecutive_errors = 5

        while self.is_running and self.is_connected:
            try:
                if not self.serial_connection or not self.serial_connection.is_open:
                    break

                line = (
                    self.serial_connection.readline()
                    .decode("utf-8", errors="ignore")
                    .strip()
                )

                if line:
                    consecutive_errors = 0  # Reset error counter
                    if self.is_valid_data_line(line):
                        self.parse_data_line(line)
                else:
                    time.sleep(0.01)

            except serial.SerialException as e:
                consecutive_errors += 1
                logger.error(
                    f"Serial error ({consecutive_errors}/{max_consecutive_errors}): {e}"
                )

                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Too many consecutive serial errors, disconnecting")
                    self.root.after(0, self.handle_connection_lost)
                    break

                time.sleep(0.1)

            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Unexpected error in data thread: {e}")

                if consecutive_errors >= max_consecutive_errors:
                    self.root.after(0, self.handle_connection_lost)
                    break

                time.sleep(0.1)

        logger.info("Data reading thread stopped")

    def is_valid_data_line(self, line: str) -> bool:
        """Check if line contains valid CSV data"""
        if not line or not "," in line:
            return False

        # Skip header/info lines
        skip_prefixes = (
            "===",
            "Time",
            "CSV",
            "Arduino",
            "Initializing",
            "System",
            "Starting",
            "---",
        )
        return not line.startswith(skip_prefixes)

    def parse_data_line(self, line: str):
        """Parse CSV data line with robust error handling"""
        try:
            parts = line.split(",")
            if len(parts) < 4:
                return

            timestamp_ms = float(parts[0])
            flow_rate = float(parts[1])
            total_volume = float(parts[2])
            status = parts[3].strip()

            current_pulses = int(parts[4]) if len(parts) > 4 else 0
            total_pulses = int(parts[5]) if len(parts) > 5 else 0

            # Convert to relative time
            timestamp = timestamp_ms / 1000.0
            if self.start_time is None:
                self.start_time = timestamp
            relative_time = timestamp - self.start_time

            # Store data with thread safety
            with self.thread_lock:
                self.timestamps.append(relative_time)
                self.flow_rates.append(flow_rate)
                self.total_volumes.append(total_volume)
                self.data_count += 1

            # Log significant events
            if current_pulses > 0:
                logger.info(
                    f"Flow detected: {flow_rate:.3f} L/min ({current_pulses} pulses)"
                )

        except (ValueError, IndexError) as e:
            logger.debug(f"Parse error for line '{line}': {e}")

    def start_animation(self):
        """Start plot animation"""
        try:
            # Initial draw to ensure canvas is ready
            self.canvas.draw()

            # Create animation with proper settings for tkinter
            self.animation = animation.FuncAnimation(
                self.fig,
                self.animate,
                interval=PLOT_REFRESH_MS,
                blit=False,
                cache_frame_data=False,
                save_count=100,
            )

            # Force initial canvas update
            self.canvas.draw_idle()
            logger.info("Animation started successfully")

        except Exception as e:
            logger.error(f"Error starting animation: {e}")

    def animate(self, frame):
        """Update plots with current data"""
        try:
            with self.thread_lock:
                if not self.timestamps:
                    # Still draw the empty graph
                    self.canvas.draw_idle()
                    return self.line1, self.line2

                times = list(self.timestamps)
                flows = list(self.flow_rates)
                volumes = list(self.total_volumes)

            # Ensure we have valid data
            if not times or not flows or not volumes:
                return self.line1, self.line2

            # Update plot data
            self.line1.set_data(times, flows)
            self.line2.set_data(times, volumes)

            # Auto-scale plots with proper X and Y axis limits
            if times and flows:
                # Set X-axis limits for both plots
                time_min = min(times)
                time_max = max(times)
                time_padding = max(
                    1.0, (time_max - time_min) * 0.05
                )  # 5% padding or at least 1 second

                self.ax1.set_xlim(time_min - time_padding, time_max + time_padding)
                self.ax2.set_xlim(time_min - time_padding, time_max + time_padding)

                # Set Y-axis limits with proper scaling
                max_flow = max(flows) if flows else 0
                max_volume = max(volumes) if volumes else 0

                # Flow rate Y-axis
                if max_flow > 0:
                    self.ax1.set_ylim(bottom=0, top=max_flow * 1.15)
                else:
                    self.ax1.set_ylim(bottom=0, top=1)

                # Volume Y-axis
                if max_volume > 0:
                    self.ax2.set_ylim(bottom=0, top=max_volume * 1.15)
                else:
                    self.ax2.set_ylim(bottom=0, top=0.1)

            # Update status display
            self.update_status(flows, volumes, times)

            # CRITICAL: Force canvas to redraw the updated plot
            self.canvas.draw_idle()

        except Exception as e:
            logger.error(f"Animation error: {e}")
            import traceback

            logger.error(traceback.format_exc())

        return self.line1, self.line2

    def update_status(self, flows, volumes, times):
        """Update status displays"""
        try:
            current_flow = flows[-1] if flows else 0
            current_volume = volumes[-1] if volumes else 0

            data_text = (
                f"Flow: {current_flow:.3f} L/min | Volume: {current_volume:.3f} L"
            )
            self.data_status.set(data_text)

            stats_text = f"Points: {len(times)} | System: {self.system}"
            self.stats_status.set(stats_text)

        except Exception as e:
            logger.error(f"Status update error: {e}")

    def handle_connection_lost(self):
        """Handle lost connection"""
        self.cleanup_connection()
        messagebox.showwarning("Connection Lost", "Connection to Arduino was lost")

    def reconnect(self):
        """Reconnect to Arduino"""
        if self.is_connected:
            self.disconnect_arduino()
            time.sleep(1)
        self.connect_arduino()

    def export_data(self):
        """Export collected data to CSV"""
        try:
            if not self.timestamps:
                messagebox.showwarning("No Data", "No data to export")
                return

            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            )

            if filename:
                with self.thread_lock:
                    with open(filename, "w") as f:
                        f.write("Time(s),FlowRate(L/min),TotalVolume(L)\\n")
                        for t, fr, tv in zip(
                            self.timestamps, self.flow_rates, self.total_volumes
                        ):
                            f.write(f"{t:.3f},{fr:.4f},{tv:.5f}\\n")

                messagebox.showinfo("Export Complete", f"Data exported to {filename}")
                logger.info(f"Data exported to {filename}")

        except Exception as e:
            error_msg = f"Export failed: {e}"
            logger.error(error_msg)
            messagebox.showerror("Export Error", error_msg)

    def show_about(self):
        """Show about dialog"""
        about_text = f"""Cross-Platform Liquid Flow Monitor
        
Version: 2.0
Platform: {platform.system()} {platform.machine()}
Python: {platform.python_version()}

Features:
• Real-time flow monitoring
• Cross-platform compatibility
• Robust error handling
• Data export capabilities

Hardware: Arduino + SEN-HZ21WA Flow Sensor"""

        messagebox.showinfo("About", about_text)

    def on_closing(self):
        """Handle application close"""
        try:
            self.is_running = False

            if self.is_connected:
                self.disconnect_arduino()

            # Wait for threads to finish
            if self.serial_thread and self.serial_thread.is_alive():
                self.serial_thread.join(timeout=1)

            logger.info("Application closed")
            self.root.quit()
            self.root.destroy()

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.root.destroy()

    def run(self):
        """Start the application"""
        try:
            logger.info("Starting Cross-Platform Flow Monitor GUI")
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Application error: {e}")
            logger.error(traceback.format_exc())


def main():
    """Main entry point"""
    print("🌊 Cross-Platform Liquid Flow Monitor")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {platform.python_version()}")
    print("=" * 50)

    try:
        app = CrossPlatformFlowMonitor()
        app.run()
    except KeyboardInterrupt:
        print("\\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logger.error("Fatal application error", exc_info=True)


if __name__ == "__main__":
    main()

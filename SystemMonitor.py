import tkinter as tk
from tkinter import ttk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time


class SystemsMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("System Resource Monitor")
        self.root.geometry("1200x900")

        # Frames
        self.info_frame = ttk.LabelFrame(self.root, text="System Information")
        self.info_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.graph_frame = ttk.LabelFrame(self.root, text="Real-Time Graphs")
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.process_frame = ttk.LabelFrame(self.root, text="Top Processes")
        self.process_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.partition_frame = ttk.LabelFrame(self.root, text="Disk partitions")
        self.partition_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # CPU, memory, disk, network, battery, and GPU labels
        self.cpu_label = ttk.Label(self.info_frame, text="CPU Usage: ", font=("Helvetica", 12))
        self.cpu_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.memory_label = ttk.Label(self.info_frame, text="Memory Usage: ", font=("Helvetica", 12))
        self.memory_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        self.disk_label = ttk.Label(self.info_frame, text="Disk Usage: ", font=("Helvetica", 12))
        self.disk_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.network_label = ttk.Label(self.info_frame, text="Network Usage (down/up): ", font=("Helvetica", 12))
        self.network_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

        self.temp_label = ttk.Label(self.info_frame, text="CPU Temperature: ", font=("Helvetica", 12))
        self.temp_label.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)

        self.battery_label = ttk.Label(self.info_frame, text="Battery status: ", font=("Helvetica", 12))
        self.battery_label.grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)

        # Initialize matplotlib figures
        self.fig, (self.ax1, self.ax2, self.ax3, self.ax4) = plt.subplots(4, 1, figsize=(10, 8))
        self.fig.tight_layout(pad=3)

        self.ax1.set_title("CPU Usage (%)")
        self.ax2.set_title("Memory Usage (%)")
        self.ax3.set_title("Disk Usage (%)")
        self.ax4.set_title("Network Usage (MB/s)")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Data lists for plotting
        self.cpu_usage_data = []
        self.memory_usage_data = []
        self.disk_usage_data = []
        self.network_down_data = []
        self.network_up_data = []
        self.time_data = []

        # Start the update thread
        self.update_thread = threading.Thread(target=self.update_data)
        self.update_thread.daemon = True
        self.update_thread.start()

        # Schedule the graph update
        self.update_graph()

    def update_data(self):
        last_net = psutil.net_io_counters()
        while True:
            # Gather system info
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
            disk_info = psutil.disk_usage('/')
            disk_usage = disk_info.percent
            net_info = psutil.net_io_counters()
            network_down = (net_info.bytes_recv - last_net.bytes_recv) / 1024 / 1024  # MB/s
            network_up = (net_info.bytes_sent - last_net.bytes_sent) / 1024 / 1024  # MB/s
            last_net = net_info

            # Update the labels
            self.cpu_label.config(text=f"CPU Usage: {cpu_usage:.1f}%")
            self.memory_label.config(text=f"Memory Usage: {memory_usage:.1f}%")
            self.disk_label.config(text=f"Disk Usage: {disk_usage:.1f}%")
            self.network_label.config(text=f"Network Usage (down/up): {network_down:.2f} MB/s / {network_up:.2f} MB/s")

            try:
                # Get CPU temp
                temp_info = psutil.sensors_temperatures().get('coretemp', [])[0]
                temp = temp_info.current if temp_info else None
                self.temp_label.config(text=f"CPU Temperature: {temp:.1f}°C" if temp else "CPU Temperature: N/A")
            except:
                self.temp_label.config(text="CPU Temperature: N/A")

            # Get battery status
            battery = psutil.sensors_battery()
            if battery:
                battery_status = f"{battery.percent}% {'Charging' if battery.power_plugged else 'Discharging'}"
                self.battery_label.config(text=f"Battery Status: {battery_status}")
            else:
                self.battery_label.config(text="Battery Status: N/A")

            # Append data for graph
            self.cpu_usage_data.append(cpu_usage)
            self.memory_usage_data.append(memory_usage)
            self.disk_usage_data.append(disk_usage)
            self.network_down_data.append(network_down)
            self.network_up_data.append(network_up)

            if len(self.time_data) == 0:
                self.time_data.append(0)
            else:
                self.time_data.append(self.time_data[-1] + 1)

            # Limit the length of data for display
            max_length = 50
            if len(self.cpu_usage_data) > max_length:
                self.cpu_usage_data.pop(0)
                self.memory_usage_data.pop(0)
                self.disk_usage_data.pop(0)
                self.network_down_data.pop(0)
                self.network_up_data.pop(0)
                self.time_data.pop(0)

            time.sleep(1)

    def update_graph(self):
        # Update line plots
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()

        self.ax1.plot(self.time_data, self.cpu_usage_data, label="CPU Usage", color='blue')
        self.ax2.plot(self.time_data, self.memory_usage_data, label="Memory Usage", color='green')
        self.ax3.plot(self.time_data, self.disk_usage_data, label="Disk Usage", color='red')
        self.ax4.plot(self.time_data, self.network_down_data, label="Download", color='purple')
        self.ax4.plot(self.time_data, self.network_up_data, label="Upload", color='orange')

        self.ax1.set_title("CPU Usage (%)")
        self.ax2.set_title("Memory Usage (%)")
        self.ax3.set_title("Disk Usage (%)")
        self.ax4.set_title("Network Usage (MB/s)")

        self.ax1.set_ylim(0, 100)
        self.ax2.set_ylim(0, 100)
        self.ax3.set_ylim(0, 100)
        self.ax4.set_ylim(0, max(max(self.network_down_data, default=1), max(self.network_up_data, default=1)))

        self.ax1.legend()
        self.ax2.legend()
        self.ax3.legend()
        self.ax4.legend()

        # Redraw the canvas
        self.canvas.draw()

        # Schedule next update
        self.root.after(1000, self.update_graph)  # Update every second


# Running the application
if __name__ == "__main__":
    root = tk.Tk()
    app = SystemsMonitor(root)
    root.mainloop()

import psutil
import requests
import socket
import time
import threading
import tkinter as tk
from tkinter import ttk
import speedtest

# Function to get local IP address and subnet mask
def get_local_ip_and_subnet():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        interfaces = psutil.net_if_addrs()
        netmask = None
        for interface in interfaces.values():
            for snic in interface:
                if snic.family == socket.AF_INET and snic.address == local_ip:
                    netmask = snic.netmask
                    break
        return local_ip, netmask
    except Exception as e:
        return "N/A", "N/A"

# Function to get global IP address
def get_global_ip():
    try:
        global_ip = requests.get('https://api.ipify.org').text
        return global_ip
    except Exception as e:
        return "N/A"

# Function to get DNS servers
def get_dns_servers():
    try:
        with open('/etc/resolv.conf', 'r') as f:
            lines = f.readlines()
        dns_servers = [line.split()[1] for line in lines if line.startswith('nameserver')]
        return dns_servers
    except Exception as e:
        return ["N/A"]

# Function to get active ports and services
def get_active_ports_and_services():
    try:
        connections = psutil.net_connections()
        active_ports_services = []
        for conn in connections:
            if conn.status == psutil.CONN_ESTABLISHED:
                try:
                    pid = conn.pid
                    process = psutil.Process(pid)
                    service = process.name()
                    active_ports_services.append(f"{conn.laddr.port}: {service}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    active_ports_services.append(f"{conn.laddr.port}: N/A")
        return active_ports_services
    except Exception as e:
        return ["N/A"]

# Function to get all established connections
def get_all_connections():
    try:
        connections = psutil.net_connections()
        connections_list = []
        for conn in connections:
            laddr_ip = conn.laddr.ip if conn.laddr else "N/A"
            laddr_port = conn.laddr.port if conn.laddr else "N/A"
            raddr_ip = conn.raddr.ip if conn.raddr else "N/A"
            raddr_port = conn.raddr.port if conn.raddr else "N/A"
            state = conn.status
            connections_list.append(f"{laddr_ip}:{laddr_port} -> {raddr_ip}:{raddr_port} [{state}]")
        return connections_list
    except Exception as e:
        return ["N/A"]

# Function to get the number of active connections
def get_active_connections_count():
    try:
        connections = psutil.net_connections()
        active_connections = [conn for conn in connections if conn.status == psutil.CONN_ESTABLISHED]
        return len(active_connections)
    except Exception as e:
        return 0

# Function to get download and upload speeds
def get_speed():
    try:
        st = speedtest.Speedtest()
        st.download()
        st.upload()
        results = st.results.dict()
        download_speed = results['download'] / 1_000_000  # Convert to Mbps
        upload_speed = results['upload'] / 1_000_000  # Convert to Mbps
        return download_speed, upload_speed
    except Exception as e:
        return "N/A", "N/A"

# Function to get interface status
def get_interface_status():
    try:
        interfaces = psutil.net_if_stats()
        interface_status = []
        for interface, stats in interfaces.items():
            status = "Up" if stats.isup else "Down"
            speed = stats.speed  # Speed in Mbps
            interface_status.append(f"{interface}: {status} (Speed: {speed} Mbps)")
        return interface_status
    except Exception as e:
        return ["N/A"]

# Function to get socket information
def get_socket_info():
    try:
        socket_info = []
        for s in psutil.net_connections(kind='inet'):
            if s.status == psutil.CONN_LISTEN:
                socket_info.append(f"Socket {s.fd}: {s.laddr.ip}:{s.laddr.port} (LISTEN)")
        return socket_info
    except Exception as e:
        return ["N/A"]

# Function to get network traffic
def get_network_traffic():
    try:
        counters = psutil.net_io_counters()
        bytes_sent = counters.bytes_sent
        bytes_recv = counters.bytes_recv
        packets_sent = counters.packets_sent
        packets_recv = counters.packets_recv
        return bytes_sent, bytes_recv, packets_sent, packets_recv
    except Exception as e:
        return "N/A", "N/A", "N/A", "N/A"

# Function to update data
def update_data():
    while True:
        local_ip, netmask = get_local_ip_and_subnet()
        global_ip = get_global_ip()
        dns_servers = get_dns_servers()
        active_ports_services = get_active_ports_and_services()
        connections_list = get_all_connections()
        active_connections_count = get_active_connections_count()
        download_speed, upload_speed = get_speed()
        interface_status = get_interface_status()
        socket_info = get_socket_info()
        bytes_sent, bytes_recv, packets_sent, packets_recv = get_network_traffic()
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        # Update data in the interface
        lbl_timestamp.config(text=f"Timestamp: {timestamp}")
        lbl_local_ip.config(text=f"Local IP: {local_ip}")
        lbl_subnet.config(text=f"Subnet Mask: {netmask}")
        lbl_global_ip.config(text=f"Global IP: {global_ip}")
        lbl_dns.config(text=f"DNS Servers: {', '.join(dns_servers)}")
        lbl_ports.config(text=f"Active Ports and Services: {', '.join(active_ports_services)}")
        lbl_connections.config(text=f"Active Connections Count: {active_connections_count}")
        lbl_download_speed.config(text=f"Download Speed: {download_speed:.2f} Mbps")
        lbl_upload_speed.config(text=f"Upload Speed: {upload_speed:.2f} Mbps")
        lbl_interfaces.config(text=f"Interface Status: {', '.join(interface_status)}")
        lbl_sockets.config(text=f"Socket Information: {', '.join(socket_info)}")
        lbl_traffic.config(text=f"Traffic: Sent: {bytes_sent/1_000_000:.2f} MB, Received: {bytes_recv/1_000_000:.2f} MB, Packets Sent: {packets_sent}, Packets Received: {packets_recv}")
        txt_connections.delete(1.0, tk.END)
        txt_connections.insert(tk.END, "\n".join(connections_list))

        time.sleep(10)

# Create the interface
root = tk.Tk()
root.title("Network Information")

# Create frames for better organization
frame_info = ttk.Frame(root, padding="10")
frame_info.pack(fill=tk.BOTH, expand=True)

frame_connections = ttk.Frame(root, padding="10")
frame_connections.pack(fill=tk.BOTH, expand=True)

# Add widgets to the info frame
lbl_timestamp = ttk.Label(frame_info, text="Timestamp: Initializing...")
lbl_timestamp.grid(row=0, column=0, sticky=tk.W, pady=2)

lbl_local_ip = ttk.Label(frame_info, text="Local IP: Initializing...")
lbl_local_ip.grid(row=1, column=0, sticky=tk.W, pady=2)

lbl_subnet = ttk.Label(frame_info, text="Subnet Mask: Initializing...")
lbl_subnet.grid(row=2, column=0, sticky=tk.W, pady=2)

lbl_global_ip = ttk.Label(frame_info, text="Global IP: Initializing...")
lbl_global_ip.grid(row=3, column=0, sticky=tk.W, pady=2)

lbl_dns = ttk.Label(frame_info, text="DNS Servers: Initializing...")
lbl_dns.grid(row=4, column=0, sticky=tk.W, pady=2)

lbl_ports = ttk.Label(frame_info, text="Active Ports and Services: Initializing...")
lbl_ports.grid(row=5, column=0, sticky=tk.W, pady=2)

lbl_connections = ttk.Label(frame_info, text="Active Connections Count: Initializing...")
lbl_connections.grid(row=6, column=0, sticky=tk.W, pady=2)

lbl_download_speed = ttk.Label(frame_info, text="Download Speed: Initializing...")
lbl_download_speed.grid(row=7, column=0, sticky=tk.W, pady=2)

lbl_upload_speed = ttk.Label(frame_info, text="Upload Speed: Initializing...")
lbl_upload_speed.grid(row=8, column=0, sticky=tk.W, pady=2)

lbl_interfaces = ttk.Label(frame_info, text="Interface Status: Initializing...")
lbl_interfaces.grid(row=9, column=0, sticky=tk.W, pady=2)

lbl_sockets = ttk.Label(frame_info, text="Socket Information: Initializing...")
lbl_sockets.grid(row=10, column=0, sticky=tk.W, pady=2)

lbl_traffic = ttk.Label(frame_info, text="Traffic: Initializing...")
lbl_traffic.grid(row=11, column=0, sticky=tk.W, pady=2)

# Add the text widget for connections to the connections frame
txt_connections = tk.Text(frame_connections, height=20, width=100)
txt_connections.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add a scrollbar for the text widget
scrollbar = ttk.Scrollbar(frame_connections, orient=tk.VERTICAL, command=txt_connections.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
txt_connections.config(yscrollcommand=scrollbar.set)

# Start the thread to update data
thread = threading.Thread(target=update_data, daemon=True)
thread.start()

# Start the main loop of the interface
root.mainloop()

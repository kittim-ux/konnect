import telnetlib
import re

host = input("Enter OLT IP: ")
port = input("Enter OLT port: ")
user = 'admin'  # Enter your username
password = 'admin'  # Enter your password

tn = telnetlib.Telnet(host, port)
tn.read_until(b"Username:")
tn.write(user.encode('ascii') + b"\n")
if password:
    tn.read_until(b"Password:")
    tn.write(password.encode('ascii') + b"\n")

tn.write("show version".encode('ascii') + b"\n")
output = tn.read_until(b"Current Time:")
output_str = output.decode('ascii')

# Extract the required information using regular expressions
device_type = re.search(r"Device Type\s+:\s+(\w+)", output_str).group(1)
bios_version = re.search(r"BIOS Version\s+:\s+([\d.]+)", output_str).group(1)
firmware_version = re.search(r"Firmware Version\s+:\s+(.+)", output_str).group(1)
serial_no = re.search(r"Serial No.\s+:\s+(\w+)", output_str).group(1)
mac_address = re.search(r"MAC Address\s+:\s+([0-9A-Fa-f.]+)", output_str).group(1)
ip_address = re.search(r"IP Address\s+:\s+([\d.]+)", output_str).group(1)
current_time = re.search(r"Current Time\s+:\s+(.+)", output_str).group(1)
uptime = re.search(r"Uptime\s+:\s+([\d-]+)\s+([\d:]+)", output_str)
uptime_days = uptime.group(1)
uptime_time = uptime.group(2)
cpu_usage = re.search(r"CPU Usage\s+:\s+(\d+)%", output_str).group(1)
memory_usage = re.search(r"Memory Usage\s+:\s+(\d+)%", output_str).group(1)

# Print the retrieved information
print("Device Type:", device_type)
print("BIOS Version:", bios_version)
print("Firmware Version:", firmware_version)
print("Serial No.:", serial_no)
print("MAC Address:", mac_address)
print("IP Address:", ip_address)
print("Current Time:", current_time)
print("Uptime:", uptime_days, uptime_time)
print("CPU Usage:", cpu_usage + "%")
print("Memory Usage:", memory_usage + "%")

tn.close()


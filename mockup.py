import json
import socket
import random
import time
from typing import Dict

# Broadcast IP and UDP port configuration
BROADCAST_IP = '192.168.56.255'
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


def generate_measurement(device: str) -> int:
    """
    Generates a simulated current measurement in amps (A) based on the device.
    
    Parameters:
        device (str): The identifier of the device (e.g., 'Ia', 'Ib', 'Ic', etc.)
        
    Returns:
        int: The simulated current measurement.
    """
    if device == "Ia" or device == "Ib":
        return int(random.gauss(3, 1))
    elif device == "Ic" or device == "Id":
        return int(random.gauss(8, 1.5))
    elif device == "Ie" or device == "If":
        return int(random.gauss(13, 2))
    elif device == "Ig" or device == "Ih":
        return int(random.gauss(18, 2.5))
    return 0

def get_device_id(device: str) -> int:
    """
    Retrieves the ID associated with a given device type.
    
    Parameters:
        device (str): The identifier of the device.
        
    Returns:
        int: The ID associated with the device.
    """
    if device in ["Ia", "Ib"]:
        return 1
    elif device in ["Ic", "Id"]:
        return 2
    elif device in ["Ie", "If"]:
        return 3
    elif device in ["Ig", "Ih"]:
        return 4
    return 0

def create_packet(device: str, measurement: int) -> Dict[str, int | str]:
    """
    Creates a JSON packet structure with the device, measurement, and associated ID.
    
    Parameters:
        device (str): The identifier of the device.
        measurement (int): The current measurement in amps.
        
    Returns:
        Dict[str, int | str]: The JSON packet structure.
    """
    return {
        "id": get_device_id(device),
        "device": device,
        "measurement[A]": measurement
    }

devices = ["Ia", "Ib", "Ic", "Id", "Ie", "If", "Ig", "Ih"]

start_time = time.time()

for _ in range(100000):
    device = random.choice(devices)
    measurement = generate_measurement(device)
    packet = create_packet(device, measurement)
    message = json.dumps(packet).encode('utf-8')
    sock.sendto(message, (BROADCAST_IP, PORT))

end_time = time.time()

average_send_time = (end_time - start_time) / 100000
print(f"Average send time per packet: {average_send_time:.6f} seconds")

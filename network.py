# network.py

import socket
from typing import Tuple

def create_udp_socket(ip: str, port: int) -> socket.socket:
    """Create and bind a UDP socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    return sock

def send_udp(sock: socket.socket, data: bytes, addr: Tuple[str, int]) -> None:
    """Send data to the given address using the provided socket."""
    sock.sendto(data, addr) 
import socket

# Set destination IP and Port
HOST = "127.0.0.1"
PORT = 9090

message = b"GREETINGS"
print(f"message: {message}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create socket for IPv4,UDP Protocol
sock.sendto(message, (HOST, PORT))

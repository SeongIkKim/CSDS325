import socket

# Set IP, Port that receive messages from clients
HOST = "127.0.0.1"
PORT = 9090

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create socket for IPv4, UDP Protocol
sock.bind((HOST, PORT))

print("Server ready ...")

while True:
    data, addr = sock.recvfrom(1024)  # buffer size 1024 bytes
    print(f"received message: {data.decode('utf-8')}")

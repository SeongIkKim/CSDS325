import argparse

from Project2.rdt_socket import RDTSocket

parser = argparse.ArgumentParser(description='Client')
parser.add_argument('-p', '--receiver_port', help='Receiver port')
parser.add_argument('-ws', '--window_size', help='Window size')

args = parser.parse_args()
RECEIVER_PORT = int(args.receiver_port)
WINDOW_SIZE = args.window_size


socket = RDTSocket(WINDOW_SIZE)
socket.bind(('127.0.0.1', RECEIVER_PORT))
socket.sender_addr = socket.accept()
total_data = socket.recv()
print(total_data)

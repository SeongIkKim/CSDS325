import argparse
import time

from rdt_socket import RDTSocket
from utility import Address

parser = argparse.ArgumentParser(description='Server')
parser.add_argument('-ip', '--receiver_ip', help='Receiver ip')
parser.add_argument('-p', '--receiver_port', help='Receiver port')
parser.add_argument('-ws', '--window_size', help='Window size')

args = parser.parse_args()
RECEIVER_IP = args.receiver_ip
RECEIVER_PORT = int(args.receiver_port)
WINDOW_SIZE = int(args.window_size)

socket = RDTSocket(WINDOW_SIZE)
socket.bind(('127.0.0.1', 23456))
socket.connect(Address(RECEIVER_IP, RECEIVER_PORT))

with open('./alice.txt', 'r') as f:
    data = f.read()
socket.send(data)
socket.close()

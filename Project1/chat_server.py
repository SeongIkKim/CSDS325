import argparse
import re
import socket
from typing import Tuple

from messages import MessageType

parser = argparse.ArgumentParser(description='Chat SERVER')
parser.add_argument('-p', '--port', help='Server listening socket port')

args = parser.parse_args()
PORT = args.port

class ChatServer:
    def __init__(self, port: int):
        self._port = port
        self._clients = set()  # greeted sender address list

    def init(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # Create socket for IPv4,UDP Protocol
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # allow multiple socket on one port
        self._sock.bind(('0.0.0.0', self._port))  # listen from any ip address, but specific port
        print("Server Initialized...")
        print(f"CREATE CHATROOM listening [port {self._port}]")

    def recv_msg(self):
        data, sender = self._sock.recvfrom(2048)  # buffer size 2048 bytes
        msg_type, content = self._parse_msg(data)

        if msg_type == MessageType.MESSAGE:
            self._broadcast(sender, content)
        elif msg_type == MessageType.GREETING:
            self._add_greeted_client(sender)
        else:
            pass  # do not handle exception case

    def _parse_msg(self, msg: bytes) -> Tuple[str, str]:
        """
        Parse datagram easy to use.
        :param msg: byte encoded message from socket
        :return: message type, message content
        """
        match = re.search(r"^\[(\w+)\](\S.*)", msg.decode())
        if not match:
            raise ValueError()
        msg_type, content = match.group(1), match.group(2)
        return msg_type, content

    def _add_greeted_client(self, sender: Tuple[str, int]):
        self._clients.add(sender)

    def _create_broadcast_message(self, sender: Tuple[str, int], msg: str):
        """
        Make formatted broadcast message.
        :param sender: UDP message sender address. Including IP, port.
        :param msg: message content
        :return: formatted binary message data
        """
        ip, port = sender
        data = f"[{MessageType.INCOMING}]<From {ip}:{port}>{msg}"
        byte_msg = data.encode()
        return byte_msg

    def _broadcast(self, sender: Tuple[str, int], msg: str):
        byte_msg = self._create_broadcast_message(sender, msg)
        for client_addr in self._clients:
            self._sock.sendto(byte_msg, client_addr)


server = ChatServer(int(PORT))
server.init()

while True:
    server.recv_msg()

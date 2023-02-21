import re
import sys
import select
import socket
import argparse
from typing import Tuple

from messages import MessageType

parser = argparse.ArgumentParser(description='Chat Client')
parser.add_argument('-ip', '--server_ip', help='Destination server ip')
parser.add_argument('-p', '--server_port', help='Destination server port')

args = parser.parse_args()
SERVER_IP = args.server_ip
SERVER_PORT = args.server_port


class ChatClient:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port

    def init(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # Create socket for IPv4,UDP Protocol
        self._sock.setblocking(False)  # use asynchronous, nonblocking socket to use select
        print(f"ENTERED CHATROOM [host {self._host} : port {self._port}]")

    def get_socket(self):
        return self._sock

    def recv_msg(self):
        """
        Get multicasted message from client socket and print it
        :return:
        """
        data, sender = self._sock.recvfrom(2048)  # buffer size 2048 bytes
        msg_type, content = self._parse_msg(data)

        if msg_type == MessageType.INCOMING:  # chat client socket only receives multicasted messages
            print(content)

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

    def _create_message(self, type: MessageType, msg: str) -> bytes:
        """
        Create formatted message that can be parsed by client, server either
        :param type: message type produced
        :param msg: message content
        :return: formatted binary message data
        """
        data = f"[{type}]{msg}"
        byte_msg = data.encode()
        return byte_msg

    def register(self):
        message = self._create_message(MessageType.GREETING, "greeting")
        self._sock.sendto(message, (self._host, self._port))

    def send_msg(self, msg: str):
        """
        Send message to destination server.
        :param msg: string message data to send.
        """
        message = self._create_message(MessageType.MESSAGE, msg)
        self._sock.sendto(message, (self._host, self._port))


client = ChatClient(SERVER_IP, int(SERVER_PORT))
client.init()
client.register()

client_sock = client.get_socket()
readers = [client_sock, sys.stdin]  # read socket from server incoming message, user input message

while True:
    read_sockets, write_sockets, error_sockets = select.select(readers, [], [])

    for sock in read_sockets:
        # client socket listening INCOMING messages
        if sock == client_sock:
            client.recv_msg()
        # sys.stdin socket listening user input
        else:
            msg = input('')
            sys.stdout.write("\033[F")  # remove input echo (move line cursor one line up)
            client.send_msg(msg)

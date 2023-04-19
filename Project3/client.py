import json
import math
import re
import sys
import select
import socket
import argparse
from typing import Tuple

from messages import MessageType

parser = argparse.ArgumentParser(description='Network Node Client')
parser.add_argument('-ip', '--server_ip', help='Remote server ip')
parser.add_argument('-p', '--server_port', help='Remote server port')

args = parser.parse_args()
SERVER_IP = args.server_ip
SERVER_PORT = args.server_port


class NodeClient:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._node_name = None
        self._neighbors = None
        self._vector = {"u": math.inf, "w": math.inf, "v": math.inf, "x": math.inf, "y": math.inf, "z": math.inf}

    def init(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # Create socket for IPv4,UDP Protocol
        self._sock.setblocking(False)  # use asynchronous, nonblocking socket to use select
        print(f"CREATE CLIENT [host {self._host} : port {self._port}]")

    def get_socket(self):
        return self._sock

    def recv_msg(self):
        """
        Get multicasted message from client socket and print it
        :return:
        """
        data, sender = self._sock.recvfrom(1476)
        msg_type, content = self._parse_msg(data)

        if msg_type == MessageType.ACCEPT:
            distance_info = json.loads(content)
            self._initialize_vector(distance_info)
        elif msg_type == MessageType.UPDATE:
            vector_info = json.loads(content)
            original_vector = self._vector.copy()
            self._update_vector(vector_info)
            if not self._vector == original_vector:
                self._broadcast_request()
        else:
            pass

    def _initialize_vector(self, distance_info):
        self._node_name = distance_info.keys()[0]
        self._neighbors = distance_info[self._node_name]
        self._vector[self._node_name] = 0
        for neighbor, distance in self._neighbors.items():
            self._vector[neighbor] = distance
        print(f"{self._node_name} - {self._vector}")

    def _update_vector(self, vector_info):
        update_request_node = vector_info.keys()[0]
        updated_vector = vector_info[update_request_node]
        print(f"Update request from [{updated_vector}] - {updated_vector}")
        for v, cost in self._vector.items():
            self._vector[v] = min(self._vector[update_request_node] + updated_vector[v], self._vector[v])
        print(f"Updated distance vector in {self._node_name} \n {self._vector}")

    def _broadcast_request(self):
        message = json.dumps({self._node_name: self._vector})
        self._send_msg(message)

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
        message = self._create_message(MessageType.JOIN, "JOIN")
        self._sock.sendto(message, (self._host, self._port))

    def _send_msg(self, msg: str):
        """
        Send message to destination server.
        :param msg: string message data to send.
        """
        message = self._create_message(MessageType.UPDATE, msg)
        self._sock.sendto(message, (self._host, self._port))


client = NodeClient(SERVER_IP, int(SERVER_PORT))
client.init()
client.register()

while True:
    client.recv_msg()

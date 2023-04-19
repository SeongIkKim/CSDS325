import argparse
import json
import re
import socket
from typing import Tuple, Dict

from messages import MessageType

parser = argparse.ArgumentParser(description='Distance routing vector algorithm server')
parser.add_argument('-p', '--port', help='Server listening socket port')

args = parser.parse_args()
PORT = args.port

class Server:
    def __init__(self, port: int):
        self._port = port
        self._addr_to_client = {} # addr -> node name
        self._clients = {
            "u": {"neighbors": {"x": 5, "w": 3, "v": 7, "y": -1, "z": -1}},
            "w": {"neighbors": {"u": 3, "x": 4, "v": 3, "y": 8, "z": -1}},
            "x": {"neighbors": {"u": 5, "w": 4, "v": -1, "y": 7, "z": 9}},
            "v": {"neighbors": {"u": 7, "x": -1, "w": 3, "y": 4, "z": -1}},
            "y": {"neighbors": {"u": -1, "x": 7, "w": 8, "v": 4, "z": 2}},
            "z": {"neighbors": {"u": -1, "x": 9, "w": -1, "v": -1, "y": 2}}
        }

        for node_name, _ in self._clients.items():
            self._clients[node_name]["ip"] = None
            self._clients[node_name]["port"] = None

    def init(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # Create socket for IPv4,UDP Protocol
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # allow multiple socket on one port
        self._sock.bind(('0.0.0.0', self._port))  # listen from any ip address, but specific port
        print("Server Initialized...")
        print(f"CREATE SERVER listening [port {self._port}]")

    def recv_msg(self):
        data, sender = self._sock.recvfrom(1472)
        msg_type, content = self._parse_msg(data)
        print(msg_type, content)

        if int(msg_type) == MessageType.JOIN:
            self._join(sender, content)
            self._accept(sender)
            if len(self._addr_to_client) == len(self._clients):
                self._establishing_complete()
        elif int(msg_type) == MessageType.UPDATE:
            self._broadcast_updated_vector(sender, content)
        else:
            pass  # do not handle exception case

    def _join(self, sender: Tuple[str, int], node_name: str):
        """
        Add sender as client node in network, then send the neighboring nodes' information.
        :param sender: sender ip addr
        :return:
        """
        # Add sender to network as client node
        if self._clients[node_name]['ip'] or self._clients[node_name]['port']:
            raise RuntimeError
        self._clients[node_name]['ip'], self._clients[node_name]['port'] = sender
        self._addr_to_client[sender] = node_name

    def _accept(self, sender):
        node_name = self._addr_to_client[sender]
        distance_info = self._get_initial_distance_info(node_name)
        byte_msg = self._create_byte_message(MessageType.ACCEPT, json.dumps(distance_info))
        self._sock.sendto(byte_msg, sender)

    def _establishing_complete(self):
        for sender in self._addr_to_client.keys():
            byte_msg = self._create_byte_message(MessageType.ESTABLISHED, "Network established. You can update distance routing vector now.")
            self._sock.sendto(byte_msg, sender)

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

    def _get_initial_distance_info(self, node_name: str) -> Dict[str, int]:
        neighbors = self._clients[node_name]["neighbors"]
        return {node_name: neighbors}

    def _create_byte_message(self, msg_type: MessageType, msg: str):
        """
        Make formatted message.
        :param msg_type: message type
        :param msg: message content
        :return: formatted binary message data
        """
        data = f"[{msg_type}]{msg}"
        byte_msg = data.encode()
        return byte_msg

    def _broadcast_updated_vector(self, sender: Tuple[str, int], msg: str):
        byte_msg = self._create_byte_message(MessageType.UPDATE, msg)
        node_name = self._addr_to_client[sender]
        neighbors = self._clients[node_name]['neighbors']
        for neighbor, distance in neighbors.items():
            if distance < 0:  # not directly connected
                continue
            neighbor_addr = (self._clients[neighbor]['ip'], self._clients[neighbor]['port'])
            self._sock.sendto(byte_msg, neighbor_addr)


server = Server(int(PORT))
server.init()

while True:
    server.recv_msg()

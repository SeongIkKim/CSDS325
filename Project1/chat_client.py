import socket

from messages import MessageType

class ChatClient:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port

    def init(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # Create socket for IPv4,UDP Protocol
        print(f"Set UDP destination server [host {self._host} : port {self._port}]")

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

client = ChatClient('224.0.0.1', 9090)
client.init()
client.register()

while True:
    input_msg = input('')
    client.send_msg(input_msg)


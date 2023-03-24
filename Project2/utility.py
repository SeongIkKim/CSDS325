from dataclasses import dataclass
import socket
from typing import Tuple, Any
import zlib


class UnreliableSocket(socket.socket):
    def __init__(self):
        super().__init__(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

    def bind(self, address: Tuple[str, int]) -> None:
        """
        Inherited from normal UDP socket
        :param address: (host, port)
        """
        super().bind(address)

    def recvfrom(self, bufsize: int, flags: int = ...) -> Tuple[bytes, Any]:
        """
        Inherited from normal UDP socket
        should simulate packet loss, packet delay, packet corruption scenarios
        :param bufsize: receive buffer size
        :param flags: flags
        :return: datagram and return address
        """
        # TODO simulate packet loss
        # TODO simulate packet delay
        # TODO simulate packet corruption
        return super().recvfrom(bufsize, flags)

    def sendto(self, data, address):
        """
        Inherited from normal UDP socket
        :param data: readable buffer data
        :param address: (host, port)
        """
        return super().sendto(data, address)

    def close(self) -> None:
        """
        Inherited from normal UDP socket
        :return:
        """
        self.close()


@dataclass
class PacketHeader:
    type: int  # 0: START; 1: END; 2: DATA; 3: ACK
    seq_num: int
    length: int  # length of data. 0 for ACK, START, END packets
    checksum: int  # 32-bit crc


def compute_checksum(bin_str: bytes):
    """
    calculate the crc32 checksum value
    :return:
    """
    return zlib.crc32(bin_str)

def verify_packet():
    """
    verifies the integrity of the received segments
    :return:
    """
    pass

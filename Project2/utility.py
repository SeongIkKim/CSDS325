import errno
import os
import signal
import struct
from dataclasses import dataclass
import socket
from functools import wraps
from typing import Tuple, Any, Optional
import zlib

from Project2.messages import PacketType


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


class PacketHeader:
    type: int  # 0: START; 1: END; 2: DATA; 3: ACK; 4: END_ACK
    seq_num: int
    length: int  # length of data. 0 for ACK, START, END packets
    checksum: int  # 32-bit crc

    def __init__(self, type: PacketType, seq_num: int, length: int = 0, checksum: int = 0):
        self.type = type
        self.seq_num = seq_num
        self.length = length
        self.checksum = checksum


class Segment:
    header: Optional[PacketHeader]
    data: str

    def __init__(self, header: PacketHeader, payload: str = ''):
        """
        Create formatted segment that can be parsed
        :param header: rdt packet header
        :param payload: segment data
        """
        bin_data = str_to_byte(payload)
        self.header = header
        self.header.length = len(bin_data),
        self.header.checksum = compute_checksum(bin_data)
        self.data = payload

    def to_bytes(self) -> bytes:
        header_bytes = struct.pack(
            '4I',
            self.header.type,
            self.header.seq_num,
            self.header.checksum,
            self.header.length
        )
        payload_bytes = str_to_byte(self.data)
        segment_bytes = header_bytes + payload_bytes
        return segment_bytes

    @classmethod
    def from_bytes(cls, segment_bytes: bytes):
        header_bytes, data_bytes = segment_bytes[:16], segment_bytes[16:]
        values = struct.unpack('4I', header_bytes)
        header = PacketHeader(*values)
        data = byte_to_str(data_bytes)
        parsed_segment = Segment(header=header, payload=data)
        return parsed_segment

@dataclass
class Address:
    ip: str
    port: int


def compute_checksum(bin_str: bytes) -> int:
    """
    calculate the crc32 checksum value
    :return:
    """
    return zlib.crc32(bin_str)


def verify_packet(segment: Segment) -> bool:
    """
    verifies the integrity of the received segments
    :return:
    """
    return compute_checksum(segment.data.encode()) == segment.header.checksum


def str_to_byte(data: str):
    return data.encode('utf-8')


def byte_to_str(byte_data: bytes):
    return byte_data.decode('utf-8')



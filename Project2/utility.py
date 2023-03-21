from dataclasses import dataclass


class UnreliableSocket:
    def bind(self):
        pass

    def recvfrom(self):
        pass

    def sendto(self):
        pass

    def close(self):
        pass


@dataclass
class PacketHeader:
    type: int  # 0: START; 1: END; 2: DATA; 3: ACK
    seq_num: int
    length: int  # length of data. 0 for ACK, START, END packets
    checksum: int  # 32-bit crc


def compute_checksum():
    pass

def verify_packet():
    pass

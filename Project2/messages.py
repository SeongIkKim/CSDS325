from enum import IntEnum


class PacketType(IntEnum):
    START = 0
    END = 1
    DATA = 2
    ACK = 3
    END_ACK = 4

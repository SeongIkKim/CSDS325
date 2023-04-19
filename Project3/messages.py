from enum import IntEnum


class MessageType(IntEnum):
    JOIN = 0
    ACCEPT = 1  # node joining request accept
    ESTABLISHED = 2  # all nodes joined
    UPDATE = 3
    END = 4

from enum import Enum


class MessageType(str, Enum):
    GREETING = 'GREETING'
    MESSAGE = 'MESSAGE'
    INCOMING = 'INCOMING'


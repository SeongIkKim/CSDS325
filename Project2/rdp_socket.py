from utility import UnreliableSocket


class RDTSocket(UnreliableSocket):
    _TIMEOUT_THRESHOLD = 500  # ms

    def accept(self):
        pass

    def connect(self):
        """
        Send START message and then wait for ACK.
        seq_num of ACK message should be the same with that of START message.
        After all, connection is open and can send additional packet messages.
        :return:
        """
        pass

    def send(self):
        pass

    def recv(self):
        pass

    def close(self):
        """
        Send END message and then wait for ACK.
        seq_num of ACK message should be the same with that of END message.
        After all, connection is closed.
        :return:
        """
        pass

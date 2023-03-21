from utility import UnreliableSocket

class RDTSocket(UnreliableSocket):
    _TIMEOUT_THRESHOLD = 500  # ms

    def accept(self):
        pass
    def connect(self):
        pass
    def send(self):
        pass
    def recv(self):
        pass
    def close(self):
        pass

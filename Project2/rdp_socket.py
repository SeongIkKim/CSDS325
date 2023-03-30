import struct
from typing import Tuple

from Project2.messages import PacketType
from utility import UnreliableSocket, PacketHeader, compute_checksum, byte_to_str, Segment, Address

SEGMENT_SIZE = 1472  # 1500 - 8(UDP header) - 20 (IP protocol)
DATA_SIZE = 1456  # 1472 - 16(Packet Header size)

class RDTSocket(UnreliableSocket):
    receiver_addr: Address  # ip, port
    sender_addr: Address  # ip, port

    window_size: int
    sent_seq_num: int  # last sent pkt sequence number. last seq num of sender window
    rcv_expected_seq_num: int = 0  # pkt sequence number that receiver expected to receive next time.
    rcv_buffer: list = []  # receiver buffer, stores pkts
    total_data: str = '' # sum of payloads

    connected: bool = False  # Is sender-receiver connection established?

    timer: float = 0.5  # second

    def __init__(self, window_size: int):
        super().__init__()
        self.window_size = window_size

    def accept(self) -> Address:
        """
        TCP-like accept function
        invoked by "receiver" to establish connections with the sender
        Wait until getting START message
        """
        print('Waiting connection request...')
        while True:
            segment_bytes, addr = self.recvfrom(SEGMENT_SIZE)
            print(f"Received packet from {addr}")
            segment = Segment.from_bytes(segment_bytes)
            if segment.header.type == PacketType.START:
                break
            print(f"Connection not established yet : dropped [{segment.header.type}] [{segment.data}]")

        # Got START message
        # create START_ACK message
        self.rcv_expected_seq_num += 1
        header = PacketHeader(PacketType.ACK, self.rcv_expected_seq_num)
        payload = ''
        packet = Segment(header, payload)
        self.sendto(packet, addr)
        print('Sent START_ACK message to sender - connection established')

        # TODO TIMEOUT CHECK

        self.connected = True
        return addr

    def connect(self, address: Address) -> None:
        """
        TCP-like connect function
        invoked by "sender" to initiate connection request with the receiver
        Send START message

        1.Waiting for ACK,
        2.checking seq_num of ACK message should be the same with that of START message,
        3.sending additional packet messages
        Above 3 actions would be implemented in recv() method.
        """
        self.receiver_addr = address
        # create & send connection request packet
        header = PacketHeader(PacketType.START, seq_num=0)
        packet = Segment(header)
        self.send(packet)
        self.sent_seq_num = 0


    def send(self, data):
        """
        invoked by sender to transmit data to the receiver
        1. split input data into appropriately sized chunks of data
        2. append a checksum(calculated by 'compute_checksum()' in utility.py) to each packet
        3. seq_num should increment by one for each additional segment in a connection.
        """
        # TODO split input data into appropriate sized chunks
        # TODO append a checksum to each packet
        # TODO add seq_num for each segment
        # TODO should use super().send_to()
        pass

    def recv(self):
        """
        invoked by the receiver to receive data from the sender
        1. reassemble the chunks
        2. check integrity of the segments by verify_packet() function in utility.py
            - If calculated checksum does not match with header checksum, then drop packet(do not send ACK)
        3. pass the message back to the application process
        Drop all packets which seq_num >= _EXPECTED_SEQ_NUM + _WINDOW_SIZE to maintain window size window.
        :return:
        """
        # TODO should use super().recv_from()
        # TODO got ACK so move forward window and reset timeout timer
        packet, sender = self.recvfrom(4096)
        header_bytes, data_bytes = packet[:16], packet[16:]
        values = struct.unpack('4I', header_bytes)
        header = PacketHeader(*values)

        if header.checksum != compute_checksum(data_bytes):
            print('Data Corrupted')
            # do not send ACK
            return

        # Received correct packet
        # TODO segment assemble and check order
        self.rcv_seq_num = max(self.rcv_seq_num, header.seq_num)

        data = byte_to_str(data_bytes)
        print(data)

        # send ACK to sender
        self._create_segment(PacketType.ACK, seq_num=self.rcv_seq_num + 1, header.seq_num)

        return

    def close(self):
        """
        invoked by the sender to terminate the connection between the sender and the receiver.
        Send END message and then wait for ACK.
        seq_num of ACK message should be the same with that of END message.
        After all, connection is closed.
        :return:
        """
        pass


import random
import struct
from typing import Tuple

from Project2.messages import PacketType
from utility import UnreliableSocket, PacketHeader, compute_checksum, byte_to_str, Segment, Address, verify_packet

SEGMENT_SIZE = 1472  # 1500 - 8(UDP header) - 20 (IP protocol)
DATA_SIZE = 1456  # 1472 - 16(Packet Header size)

class RDTSocket(UnreliableSocket):
    receiver_addr: Address  # ip, port
    sender_addr: Address  # ip, port

    window_size: int
    sent_seq_num: int  # last sent pkt sequence number. last seq num of sender window
    rcv_expected_seq_num: int  # pkt sequence number that receiver expected to receive next time.
    out_of_order_pkts: list = []  # receiver buffer, stores out of order packets
    buffered_pkt_seq_nums: set = {} # out of order packets seq nums set
    total_data: str = '' # sum of payloads

    connected: bool = False  # Is sender-receiver connection established?

    timer: float = 0.5  # second

    def __init__(self, window_size: int):
        super().__init__()
        self.window_size = window_size
        self.sent_seq_num = 0

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
            print(f"Connection not established yet : dropped [{segment.header.type}] [{segment.header.seq_num}] [{segment.data}]")

        # Got START message
        # create START_ACK message
        self.rcv_expected_seq_num = 1
        header = PacketHeader(PacketType.ACK, segment.header.seq_num)  # Set START_ACK seq_num same with START msg
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
        Waiting for ACK
        Checking seq_num of ACK message should be the same with that of START message
        """
        print(f'Try to connect with {address}...')
        self.receiver_addr = address
        # create & send connection request packet
        random_seq_num = random.randint(1, 100)
        header = PacketHeader(PacketType.START, seq_num=random_seq_num)
        packet = Segment(header)
        self.sendto(packet, self.receiver_addr)

        while True:
            segment_bytes, sender = self.recvfrom(SEGMENT_SIZE)
            segment = Segment.from_bytes(segment_bytes)
            if not verify_packet(segment):
                # Drop and do not send ACK
                print(f'seq_num [{segment.header.seq_num}] - Data Corrupted. Drop Packet')
                continue

            if segment.header.type == PacketType.ACK and segment.header.seq_num == random_seq_num:
                print('Connection established.')
                break
            else:
                print(f'Drop packet - packet type [{segment.header.type}], not START_ACK')


    def send(self):
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


    def recv(self):
        """
        invoked by the receiver to receive data from the sender
        1. reassemble the chunks
        2. check integrity of the segments by verify_packet() function in utility.py
            - If calculated checksum does not match with header checksum, then drop packet(do not send ACK)
        3. pass the message back to the application process
        Drop all packets which seq_num >= EXPECTED_SEQ_NUM + WINDOW_SIZE to maintain window size window.
        :return:
        """
        # TODO got ACK so move forward window and reset timeout timer
        if not self.connected or not self.sender_addr:
            print('Connection is not established properly yet. Cannot receive data')
            return

        # Receive all segments and assemble

        while True:
            segment_bytes, sender = self.recvfrom(SEGMENT_SIZE)
            segment = Segment.from_bytes(segment_bytes)
            if not verify_packet(segment):
                # Drop and do not send ACK
                print(f'seq_num [{segment.header.seq_num}] - Data Corrupted. Drop Packet')
                continue

            # Received uncorrupted packet

            # 1. connection end message
            if segment.header.type == PacketType.END:
                if segment.header.seq_num != self.rcv_expected_seq_num:
                    print(f'Drop END message packet [{segment.header.seq_num}] - Transferring packet missed. Receiving not done yet')
                header = PacketHeader(type=PacketType.END_ACK, seq_num=segment.header.seq_num)
                segment = Segment(header, '')
                self.sendto(segment, self.sender_addr)

                self.rcv_expected_seq_num += 1
                self.connected = False
                break  # The only way to break the whole loop - receiving done, connection closed

            # 2. data messsage
            elif segment.header.type == PacketType.DATA:
                # out of order packet
                if self.rcv_expected_seq_num != segment.header.seq_num:
                    if segment.header.seq_num >= self.rcv_expected_seq_num + self.window_size: # over window size
                        print(f'Dropped packet [{segment.header.seq_num}] over window [{self.rcv_expected_seq_num} ~ {self.rcv_expected_seq_num + self.window_size}]')
                        continue
                    elif segment.header.seq_num in self.buffered_pkt_seq_nums:
                        print(f'Dropped packet [{segment.header.seq_num}] already buffered')
                        continue
                    else: # in window size and newly received
                        self.out_of_order_pkts.append(segment)
                        self.buffered_pkt_seq_nums.add(segment.header.seq_num)
                        header = PacketHeader(type=PacketType.ACK, seq_num=self.rcv_expected_seq_num) # send duplicated ACK
                        segment = Segment(header, '')
                        self.sendto(segment, self.sender_addr)
                # correct order packet
                else:
                    self.total_data += segment.data # assemble
                    self.rcv_expected_seq_num += 1
                    self.out_of_order_pkts.sort(key=lambda segment: segment.header.seq_num)

                    while self.out_of_order_pkts:
                        # there is another missing pkt in out of order packets
                        if self.out_of_order_pkts[0].header.seq_num != self.rcv_expected_seq_num:
                            break

                        pkt = self.out_of_order_pkts.pop()  # next packet
                        self.total_data += pkt.data
                        self.rcv_expected_seq_num += 1

                    header = PacketHeader(type=PacketType.ACK, seq_num=self.rcv_expected_seq_num)
                    segment = Segment(header, '')
                    self.sendto(segment, self.sender_addr)

        return self.total_data

    def close(self):
        """
        invoked by the sender to terminate the connection between the sender and the receiver.
        Send END message and then wait for ACK.
        seq_num of ACK message should be the same with that of END message.
        After all, connection is closed.
        :return:
        """
        # create & send connection request packet
        header = PacketHeader(PacketType.END, seq_num=self.sent_seq_num + 1)
        end_msg = Segment(header, '')
        self.sendto(end_msg, self.receiver_addr)
        self.sent_seq_num += 1

        while True:
            segment_bytes, sender = self.recvfrom(SEGMENT_SIZE)
            segment = Segment.from_bytes(segment_bytes)
            if not verify_packet(segment):
                # Drop and do not send ACK
                print(f'seq_num [{segment.header.seq_num}] - Data Corrupted. Drop Packet')
                continue

            if segment.header.type == PacketType.END_ACK and segment.header.seq_num == self.sent_seq_num:
                print('Transferring is done. Connection closed.')
                break
            else:
                print(f'Drop packet - packet type [{segment.header.type}], not END_ACK')

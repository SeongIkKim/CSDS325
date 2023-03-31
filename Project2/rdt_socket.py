import random
import time
from typing import Tuple

from Project2.messages import PacketType
from utility import UnreliableSocket, PacketHeader, byte_to_str, Segment, Address, verify_packet, str_to_byte

SEGMENT_SIZE = 1472  # 1500 - 8(UDP header) - 20 (IP protocol)
DATA_SIZE = 1456  # 1472 - 16(Packet Header size)

class RDTSocket(UnreliableSocket):
    receiver_addr: Address  # ip, port
    sender_addr: Address  # ip, port

    window_size: int
    window_boundary: Tuple[int, int]  # window boundary - (start, end + 1)
    sent_seq_num: int  # last sent pkt sequence number. last seq num of sender window
    rcv_expected_seq_num: int  # pkt sequence number that receiver expected to receive next time.
    out_of_order_pkts: list = []  # receiver buffer, stores out of order packets
    buffered_pkt_seq_nums: set = {} # out of order packets seq nums set
    total_data_bytes: bytes = b'' # sum of payloads
    total_data: str = ''

    connected: bool = False  # Is sender-receiver connection established?

    timer: float = 0.5  # second

    def __init__(self, window_size: int):
        super().__init__()
        self.settimeout(self.timer) # socket timer setup. Later check again for case that did not get ACK message
        self.sent_seq_num = -1
        self.window_size = window_size
        self.window_boundary = (0, window_size)

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


    def send(self, data: str):
        """
        invoked by sender to transmit data to the receiver
        1. split input data into appropriately sized chunks of data
        2. append a checksum(calculated by 'compute_checksum()' in utility.py) to each packet
        3. seq_num should increment by one for each additional segment in a connection.
        """
        if not self.connected or not self.receiver_addr:
            print('Connection not established yet.')
            return

        data_bytes = str_to_byte(data)

        # split whole data to chunks
        chunks = []
        for i in range(0, len(data_bytes), DATA_SIZE):
            header = PacketHeader(type=PacketType.DATA, seq_num=i+1)
            data = byte_to_str(data_bytes[i:i + DATA_SIZE])
            segment = Segment(header, data)
            chunks.append(segment)

        last_ack_num = 0

        # send chunks in order
        while last_ack_num <= chunks[-1].header.seq_num:
            window = chunks[self.window_boundary[0] : self.window_boundary[2]]
            for chunk in window:
                self.sendto(chunk, self.receiver_addr)
                self.sent_seq_num += 1
                print(f'Sent chunk seq_num [{chunk.header.seq_num}]')

            last_ack_time = time.time()
            window_ack_count = 0
            while window_ack_count < self.window_size:
                if time.time() - last_ack_time > self.timer:
                    print('Timeout error')
                    # break and go to outer while loop(send whole unacknowledged window packets again)
                    break
                segment_bytes, sender = self.recvfrom(SEGMENT_SIZE)
                segment = Segment.from_bytes(segment_bytes)

                if segment.header.type != PacketType.ACK:
                    print('Drop packet - Not ACK type')
                    continue

                # Right next ack received 0 - window moves forward
                if segment.header.seq_num == last_ack_num + 1:
                    print(f'Received ACK [{segment.header.seq_num}] - window moves forward [({self.window_boundary[0]}~{self.window_boundary[1]})]')
                    last_ack_time = time.time()  # so update timer
                    last_ack_num += 1
                    self.window_boundary[0] += 1
                    self.window_boundary[1] += 1
                    window_ack_count += 1
                else:
                    print(f'Drop ACK packet - expected[{last_ack_num + 1}], but got [{segment.header.seq_num}]')

        print('Transmitting data done')


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
                    self.total_data_bytes += bytes(segment.data) # assemble
                    self.rcv_expected_seq_num += 1
                    self.out_of_order_pkts.sort(key=lambda segment: segment.header.seq_num)

                    while self.out_of_order_pkts:
                        # there is another missing pkt in out of order packets
                        if self.out_of_order_pkts[0].header.seq_num != self.rcv_expected_seq_num:
                            break

                        pkt = self.out_of_order_pkts.pop()  # next packet
                        self.total_data_bytes += bytes(pkt.data)
                        self.rcv_expected_seq_num += 1

                    header = PacketHeader(type=PacketType.ACK, seq_num=self.rcv_expected_seq_num)
                    segment = Segment(header, '')
                    self.sendto(segment, self.sender_addr)

        self.total_data = byte_to_str(self.total_data_bytes)
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
                break
            else:
                print(f'Drop packet - packet type [{segment.header.type}], not END_ACK')

        print('Transmitting is done. Connection closed.')

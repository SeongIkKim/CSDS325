import argparse

parser = argparse.ArgumentParser(description='Server')
parser.add_argument('-ip', '--receiver_ip', help='Receiver ip')
parser.add_argument('-p', '--receiver_port', help='Receiver port')
parser.add_argument('-ws', '--window_size', help='Window size')

args = parser.parse_args()
RECEIVER_IP = args.receiver_ip
RECEIVER_PORT = args.receiver_port
WINDOW_SIZE = args.window_size

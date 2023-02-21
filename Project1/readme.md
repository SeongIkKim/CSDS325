# Project 1 : Chat Application

## Quick Start

```bash
# 1. Run Chat Server first
$ python chat_server.py -ip <server ip> -p <server port>
ex) python chat_server.py -p 9090

# 2. Run multiple Chat Clients
$ python chat_client.py -ip <server ip> -p <server port>
$ python chat_client.py -ip <server ip> -p <server port>
.
.
.
ex) python chat_client.py -ip 224.0.0.1 -p 9090

# 3. Enter user input in one of Chat Client
# 4. Check other Chat Clients got broadcasted message(same Ip and Port should be specified)
```

## Dependency
- python 3.8.5
- macOS 11.4


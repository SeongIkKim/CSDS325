# Project 3 : Distance routing vector algorithm

## Quick Start

```bash
# 1. Run Server first
$ python server.py -p <server port>
ex) python chat_server.py -p 5555 -n u


# 2. Run all node clients. You should make all clients in candidates.
# Be quick since client socket has timeout timer for 30 secs.
$ python chat_client.py -ip <server ip> -p <server port> -n <node_name>
$ python chat_client.py -ip <server ip> -p <server port> -n <node_name>
.
.
.
ex) python chat_client.py -ip 127.0.0.1 -p 5555 -n u
### node name can be one of <u, v, w, x, y, z>. Duplicate node name will cause error.

# 3. After all node clients are registered, automatically network clients update their distance routing vector.
# 4. You can see the result in console. The last updated distance vector is final vector for each node.
# 30 sec after all updating is done, clients will automatically close connection and terminate.  
```

## Dependency
- python 3.8.5
- macOS 11.4

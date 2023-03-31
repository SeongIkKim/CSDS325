# Project 2 - Reliable Data Transfer

## how to use

```bash
$ python3 receiver.py -p <some_port> -ws <window_size>
# ex) python3 receiver.py -p 5341 -ws 5

$ python3 sender.py -ip <ip_address> -p <some_port> -ws <window_size>
# ex) python3 sender.py -ip 127.0.0.1 -p 5341 -ws 5

# check transmission is correct
$ diff alice.txt download.txt
# if nothing come out, it succeeds
```

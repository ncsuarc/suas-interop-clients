from __future__ import print_function
import json
import zmq
import ARC
import math
import argparse
import sys

from ARC.interop import Interop

host = "192.168.1.130"
port = "8000"
username = "testuser"
password = "testpass"

if __name__ == "__main__":
    io = Interop(host, port, username, password)
    try:
        targets = io.get_targets()
        print('\nTargets:')
        for target in targets:
            print(target)
    except KeyboardInterrupt:
        pass
    finally:
        pass

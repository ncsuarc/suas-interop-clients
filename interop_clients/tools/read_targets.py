from __future__ import print_function

import argparse
import json
import math
import sys

import ARC
import zmq
from ARC.interop import Interop

host = "192.168.1.130"
port = "8000"
username = "testuser"
password = "testpass"

if __name__ == "__main__":
    io = Interop(host, port, username, password)
    try:
        targets = io.get_targets()
        print("\nTargets:")
        for target in targets:
            print(target)
    except KeyboardInterrupt:
        pass
    finally:
        pass

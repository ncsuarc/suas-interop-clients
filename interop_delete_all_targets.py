from __future__ import print_function
import json
import zmq
import ARC
import math
import argparse
import sys

from interop import InterOp

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u","--username", required=True)
    parser.add_argument("-p","--password", required=True)
    parser.add_argument("-ip","--ip", required=True)
    parser.add_argument("-port","--port", required=True)
    parser.add_argument("-auto", "--auto", action="store_true")
    args = parser.parse_args()
    io = InterOp(args.username, args.password, args.ip, args.port)
    try:
        targets = io.get_targets()
        for target in targets:
            print('Deleting:')
            print(target)
            print('\n')
            if (not args.auto) and target.get('autonomous'):
                continue
            io.delete_target(target.get('id'))
    except KeyboardInterrupt:
        pass
    finally:
        pass

from __future__ import print_function
import json
import zmq
import ARC
import math
import argparse
import sys

from ARC.interop import Interop

if __name__ == "__main__":
    io = Interop()
    try:
        targets = io.get_targets()
        print('\nTargets:')
        for target in targets:
            print(target)
    except KeyboardInterrupt:
        pass
    finally:
        pass

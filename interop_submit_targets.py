from __future__ import print_function
import json
import ARC
import argparse
import os

from ARC.interop import Interop

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--directory", required=True)
    args = parser.parse_args()
    io = Interop()
    try:
        for objfile in os.listdir(args.directory):
            if objfile.endswith('json'):
                name = objfile.split('.')[0]
                with open(os.path.join(args.directory, objfile), 'r') as json_file:
                    json_data = json.load(json_file)
                with open(os.path.join(args.directory, name + '.jpg'), 'rb') as image_data:
                    io.post_target(json_data, image_data)
    except KeyboardInterrupt:
        pass
    finally:
        pass

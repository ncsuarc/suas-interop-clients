from __future__ import print_function

import argparse
import json
import os

import ARC
from ARC.interop import Interop

host = "192.168.1.130"
port = "8000"
username = "testuser"
password = "testpass"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", required=True)
    args = parser.parse_args()
    io = Interop(host, port, username, password)
    try:
        for objfile in os.listdir(args.directory):
            if objfile.endswith("json"):
                name = objfile.split(".")[0]
                with open(
                    os.path.join(args.directory, objfile), "r"
                ) as json_file:
                    json_data = json.load(json_file)
                    json_data = {
                        "mission": 1,
                        "type": json_data["type"].upper(),
                        "latitude": json_data["latitude"],
                        "longitude": json_data["longitude"],
                        "orientation": json_data["orientation"].upper(),
                        "shape": json_data["shape"].upper(),
                        "shapeColor": json_data["background_color"].upper(),
                        "alphanumeric": json_data["alphanumeric"],
                        "alphanumericColor": json_data[
                            "alphanumeric_color"
                        ].upper(),
                        "autonomous": False,
                    }
                with open(
                    os.path.join(args.directory, name + ".jpg"), "rb"
                ) as image_data:
                    io.post_target(json_data, image_data)
    except KeyboardInterrupt:
        pass
    finally:
        pass

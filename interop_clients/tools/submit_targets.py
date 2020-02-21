from __future__ import print_function

import json
import os

from interop_clients import Interop


def run(io: Interop, directory: str) -> None:
    try:
        for objfile in os.listdir(directory):
            if objfile.endswith("json"):
                name = objfile.split(".")[0]
                with open(os.path.join(directory, objfile), "r") as json_file:
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
                    os.path.join(directory, name + ".jpg"), "rb"
                ) as image_data:
                    io.post_target(json_data, image_data)
    except KeyboardInterrupt:
        pass
    finally:
        pass

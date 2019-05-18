from __future__ import print_function
import json
import sys
import zmq
import ARC
import math
import datetime
import argparse
import sys

from ARC.interop import Interop

telemetry_pub = "ipc:///tmp/mavlink_pub"



def generate_lat_lon(telem):
    return telem.sensors.gps.lat, telem.sensors.gps.lon, (telem.sensors.gps.alt*3.28084), (telem.sensors.gps.heading*57.2958)

if __name__ == "__main__":
    io = Interop()
    try:
        zmq_context = zmq.Context()

        # Subscribe to telemetry data
        telemetry = zmq_context.socket(zmq.SUB)
        telemetry.connect(telemetry_pub)
        telemetry.setsockopt(zmq.SUBSCRIBE, "")
        while True:
            #get the telemetry packet
            packet = telemetry.recv_json()
            telem = ARC.Telemetry(packet["telemetry"])

            #generate and print the NMEA sentences
            lat, lon, alt, heading = generate_lat_lon(telem)

            io.send_coord(lat, lon, alt, heading)
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        telemetry.close()
        zmq_context.term()

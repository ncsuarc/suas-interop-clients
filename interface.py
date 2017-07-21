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

piccolo_pub = "ipc:///tmp/piccolo_pub"



def generate_lat_lon(telem):
    return telem.sensors.gps.lat, telem.sensors.gps.lon, (telem.sensors.gps.alt*3.28084), (telem.sensors.gps.heading*57.2958)

if __name__ == "__main__":
    io = Interop()
    try:
        zmq_context = zmq.Context()

        # Subscribe to Piccolo data
        piccolo = zmq_context.socket(zmq.SUB)
        piccolo.connect(piccolo_pub)
        piccolo.setsockopt(zmq.SUBSCRIBE, "")
        while True:
            #get the telemetry packet
            packet = piccolo.recv_json()
            telem = ARC.Telemetry(packet["telemetry"])
            
            #generate and print the NMEA sentences
            lat, lon, alt, heading = generate_lat_lon(telem)

            io.send_coord(lat, lon, alt, heading)
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        piccolo.close()
        zmq_context.term()
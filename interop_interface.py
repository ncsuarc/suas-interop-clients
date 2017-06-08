from __future__ import print_function
import json
import sys
import zmq
import ARC
import math
import datetime
import argparse
import sys

from interop import InterOp

piccolo_pub = "ipc:///tmp/piccolo_pub"



def generate_lat_lon(telem):
    return telem.sensors.gps.lat, telem.sensors.gps.lon, (telem.sensors.gps.alt*3.28084), (telem.sensors.gps.heading*57.2958)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u","--username", required=True)
    parser.add_argument("-p","--password", required=True)
    parser.add_argument("-ip","--ip", required=True)
    parser.add_argument("-port","--port", required=True)
    args = parser.parse_args()
    io = InterOp(args.username, args.password, args.ip, args.port)
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
        missions = io.get_missions()
        print('\nMission 0')
        print(missions[0])

        print('\nEmergent')
        print(missions[0].get('emergent_last_known_pos'))

        print('\nOff-Axis')
        print(missions[0].get('off_axis_target_pos'))

        print('\nAir Drop')
        print(missions[0].get('air_drop_pos'))

        obstacles = io.get_obstacles()
        print('\nStationary')
        print(obstacles)
        print('\nStationary')
        print(obstacles.get('stationary_obstacles'))
        print('\nMoving')
        print(obstacles.get('moving_obstacles'))
        piccolo.close()
        zmq_context.term()

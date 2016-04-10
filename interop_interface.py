from __future__ import print_function
import json
import requests
import sys
import zmq
import ARC
import math
import datetime
import argparse
import sys

piccolo_pub = "ipc:///tmp/piccolo_pub"



def generate_lat_lon(telem):
    return telem.sensors.gps.lat, telem.sensors.gps.lon, (telem.sensors.gps.alt*3.28084), (telem.sensors.gps.heading*57.2958)


class InterOp(object):
    """Send plane location

    """
    def __init__(self, username, password, ip, port):
        self.session = requests.session()
        self.ip = ip
        self.port = port
        payload = {'username': username, 'password': password}
        response = self.session.post("http://%s:%s/api/login"%(self.ip, self.port), data = payload, timeout = 5)
        print(response.text)

    def server_info(self):
        server_info = self.session.get('http://%s:%s/api/server_info'%(self.ip, self.port))
        #print(server_info.json())
        print(server_info.text)

    def get_obstacles(self):
        obstacles = self.session.get('http://%s:%s/api/obstacles'%(self.ip, self.port))
        return obstacles.json()

    def send_coord(self, lat, lon, alt, heading):
        coord = {'latitude': lat, 'longitude': lon, 'altitude_msl': alt, 'uas_heading': heading}
        plane_location = self.session.post("http://%s:%s/api/telemetry"%(self.ip, self.port), data = coord)
        print(plane_location.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u","--username", required=True)
    parser.add_argument("-p","--password", required=True)
    parser.add_argument("-ip","--ip", required=True)
    parser.add_argument("-port","--port", required=True)
    args = parser.parse_args()
    #print(username, password, ip)
    io = InterOp(args.username, args.password, args.ip, args.port)
    #io.server_info()
    #io.get_obstacles()
    #io.send_coord()
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
        io.server_info()
        obstacles = io.get_obstacles()
        print(obstacles)
        print('\nStationary')
        print(obstacles.get('stationary_obstacles'))
        print('\nMoving')
        print(obstacles.get('moving_obstacles'))
        piccolo.close()
        zmq_context.term()

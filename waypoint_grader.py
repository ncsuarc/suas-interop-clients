from ARC import unitconversion as uc

import ARC
import argparse
import zmq
import csv
import pyproj
import math

piccolo_pub = 'ipc:///tmp/piccolo_pub'

class Waypoint():
    def __init__(self, lat, lon, alt):
        self.lat = lat
        self.lon = lon
        self.alt = alt

def generate_lat_lon(telem):
    """
    Looks up the needed data from the telemetry packet

    Arguments:
        telem: piccolo telemetry packet

    Returns:
        lat: gps latitude
        lon: gps longitude
        alt: gps altitude
    """
    lat = telem.sensors.gps.lat
    lon = telem.sensors.gps.lon
    alt = uc.m_to_ft(telem.sensors.gps.alt)
    return lat, lon, alt

def csv_to_waypoints(file):
    """
    Opens a comma seperated file and gets the waypoints

    Arguments:
        file: name of the file to open

    Returns:
        waypoints: list of waypoints
    """
    with open(file, 'r') as csvfile:
        waypoints = []
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            waypoints.append(Waypoint(float(row[0]), float(row[1]), float(row[2])))
        return waypoints

def waypoint_check(waypoints, max_dist=100, max_alt_delta=100):
    """
    Checks that the plane flies the waypoints in order and within the specified deltas

    Arguments:
        waypoints: list of waypoints
        max_dist: the maximum distance the plane can be from the waypoint to capture it
        max_alt_delta: the maximum altitude difference between the waypoint and the plane to capture

    Returns:
        None
    """
    try:
        zmq_context = zmq.Context()
        piccolo = zmq_context.socket(zmq.SUB)
        piccolo.connect(piccolo_pub)
        piccolo.setsockopt(zmq.SUBSCRIBE, "")
        for waypoint in waypoints:
            good = False
            print(waypoint.lat, waypoint.lon)
            way_location = ARC.presets.get_location(waypoint.lat, waypoint.lon)
            way_coord = pyproj.transform(ARC.presets.wgs84,
                                            way_location.projection,
                                            waypoint.lon,
                                            waypoint.lat)
            while good == False:
                packet = piccolo.recv_json()
                telem = ARC.Telemetry(packet["telemetry"])
                air_lat, air_lon, air_alt = generate_lat_lon(telem)
                air_coord = pyproj.transform(ARC.presets.wgs84,
                                                way_location.projection,
                                                air_lon,
                                                air_lat)
                delta = (way_coord[0] - air_coord[0],
                        way_coord[1] - air_coord[1])
                dist = math.sqrt(delta[0]**2 + delta[1]**2)
                dist = uc.m_to_ft(dist)
                alt_delta = abs(waypoint.alt - air_alt)
                if dist < max_dist and alt_delta < max_alt_delta:
                    print("~~~~~~~~~WAYPOINT MET~~~~~~~~~~")
                    good = True
                print(dist, alt_delta)
    except KeyboardInterrupt:
        pass
    finally:
        piccolo.close()
        zmq_context.term()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Judges waypoint accuracy')
    parser.add_argument('-f', '--file', type=str, required=True, help="Waypoint file in csv format")
    args = parser.parse_args()
    waypoints = csv_to_waypoints(args.file)
    waypoint_check(waypoints)
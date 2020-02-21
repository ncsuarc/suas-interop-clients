from __future__ import print_function

import sys

import zmq

import ARC
import ARC.unitconversion as uc
from interop_clients import Interop

telemetry_pub = "ipc:///tmp/mavlink_pub"


def generate_lat_lon(telem):
    """
    Return a tuple of coordinates from a specific ARC.Telemery.

    Args:
        telem (ARC.Telemetry): The telemetry datapoint to find the
            coordinates of.

    Returns:
        float: Latitude (degrees).
        float: Longitude (degrees).
        float: MSL Altitude (feet).
        float: Heading from north (degrees).
    """
    return (
        telem.sensors.gps.lat,
        telem.sensors.gps.lon,
        uc.m_to_ft(telem.sensors.gps.alt),
        telem.sensors.gps.heading,
    )


def run(io: Interop, telemetry_pub: str) -> None:
    try:
        zmq_context = zmq.Context()

        # Subscribe to telemetry data
        telemetry = zmq_context.socket(zmq.SUB)
        telemetry.connect(telemetry_pub)
        telemetry.setsockopt(zmq.SUBSCRIBE, "")
        while True:
            # get the telemetry packet
            packet = telemetry.recv_json()
            telem = ARC.Telemetry(packet["telemetry"])

            # generate and print the NMEA sentences
            lat, lon, alt, heading = generate_lat_lon(telem)
            print(lat, lon, alt, heading)

            io.send_coord(lat, lon, alt, heading)
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        telemetry.close()
        zmq_context.term()

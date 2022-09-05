from dronekit import connect
import atexit
import time
from interop_clients import InteropClient
from interop_clients.api import Telemetry


class TelemtrySubmitter(object):
    def __init__(self, mavlink_url: str, client: InteropClient) -> None:
        self.client = client

        self.vehicle = connect(mavlink_url, wait_ready=False)
        atexit.register(self.vehicle.close)
        self.vehicle.wait_ready(True, raise_exception=False)
        self.vehicle.add_message_listener(
            "GLOBAL_POSITION_INT", self.send_telemetry
        )

    def send_telemetry(self, vehicle, attr_name: str, m):
        t = Telemetry(
            latitude=_mavlink_latlon(m.lat),
            longitude=_mavlink_latlon(m.lon),
            altitude=_mavlink_alt(m.alt) - 142,
            heading=_mavlink_heading(m.hdg),
        )
        print("POST telemetry")
        self.client.post_telemetry(t)

def _mavlink_latlon(degrees):
    """Converts a MAVLink packet lat/lon degree format to decimal degrees."""
    return float(degrees) / 1e7


def _mavlink_alt(dist):
    """Converts a MAVLink packet millimeter format to decimal feet."""
    return dist * 0.00328084


def _mavlink_heading(heading):
    """Converts a MAVLink packet heading format to decimal degrees."""
    return heading / 100.0

if __name__ == "__main__":
    print("Connecting to interop")
    ic = InteropClient("http://10.10.130.10:80", "north-carolina-state-university", "4184601216")
    print("Connecting to plane")
    ts = TelemtrySubmitter("192.168.1.80:5601", ic)
    print("Submitting telem")
    while True:
        time.sleep(10)
        

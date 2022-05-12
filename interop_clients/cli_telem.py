from dronekit import connect
import click
import atexit
import time
from interop_clients import InteropClient
from interop_clients.api import Telemetry


class TelemtrySubmitter(object):
    def __init__(self, mavlink_url: str, client: InteropClient) -> None:
        self.client = client

        click.echo("Connecting to plane")
        self.vehicle = connect(mavlink_url, wait_ready=False)
        atexit.register(self.vehicle.close)
        self.vehicle.wait_ready(True, raise_exception=False)
        click.echo("Beginning telemtry submission")
        self.vehicle.add_message_listener(
            "GLOBAL_POSITION_INT", self.send_telemetry
        )

    def send_telemetry(self, attr_name: str, m):
        click.echo(attr_name, m)
        t = Telemetry(
            latitude=_mavlink_latlon(m.lat),
            longitude=_mavlink_latlon(m.lon),
            altitude=_mavlink_alt(m.alt),
            heading=_mavlink_heading(m.hdg),
        )
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

@click.group()
def main() -> None:
    """Submit Telemetry data
    """

@main.command("submit")
@click.option(
    "--mavlink-url",
    "-m",
    type=str,
    help="Mavlink device name to read from. E.g. tcp:localhost:8080.",
    default="udp:0.0.0.0:5601",
)
@click.pass_context
def submit_telemtry(ctx: click.Context, mavlink_url: str):
    client = ctx.obj
    TelemtrySubmitter(mavlink_url, client)

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        pass

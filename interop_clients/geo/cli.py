import click

from interop_clients.geo import boundary


@click.group()
def main() -> None:
    """
    Subcommand for interop_clients.geo.
    """


@main.command("in-search")
@click.argument("mission_id", type=int)
@click.argument("lat", type=float)
@click.argument("lon", type=float)
@click.pass_context
def in_search(
    ctx: click.Context, mission_id: int, lat: float, lon: float
) -> None:
    """Check if LAT and LON are within active mission boundaries.
    """
    client = ctx.obj
    click.echo("Is the point within the boundaries? ", nl=False)
    if boundary.in_search_grid(client.get_mission(mission_id), lat, lon):
        click.secho("Yes", fg="blue")
    else:
        click.secho("No", fg="red")

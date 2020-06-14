import click

from interop_clients.geo import boundary


@click.group()
def main() -> None:
    """
    Subcommand for interop_clients.geo.
    """


@main.command("check")
@click.argument("lat", type=float)
@click.argument("lon", type=float)
@click.pass_context
def check_point(ctx: click.Context, lat: float, lon: float) -> None:
    """
    Check if LAT and LON are within active mission boundaries.
    """
    client = ctx.obj
    click.echo("Is the point within the boundaries? ", nl=False)
    if boundary.check_point(client, lat, lon):
        click.secho("Yes", fg="blue")
    else:
        click.secho("No", fg="red")

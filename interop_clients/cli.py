import click

import interop_clients.cli_odlc
from interop_clients import InteropClient, tools


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"interop_clients v{interop_clients.__version__}")
    ctx.exit()


@click.group()
@click.option(
    "--version",
    "-V",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
)
@click.option(
    "-u",
    "--host-url",
    required=True,
    type=str,
    help="The host server to connect to.",
)
@click.option(
    "-n",
    "--username",
    required=True,
    type=str,
    help="The username to connect under.",
)
@click.password_option(
    "-p", "--password", type=str, help="The password for the session.",
)
@click.pass_context
def main(
    ctx: click.Context, host_url: str, username: str, password: str,
) -> None:
    ctx.obj = InteropClient(host_url, username, password)


@main.command("info")
@click.argument("save", type=bool)
@click.argument("interval", type=float)
@click.argument("record_time", type=int)
@click.argument("save_directory", type=str)
@click.argument("csv", type=str)
@click.pass_context
def get_info(
    ctx: click.Context,
    save: bool,
    interval: float,
    record_time: int,
    save_directory: str,
    csv: str,
) -> None:
    client = ctx.obj
    tools.get_info.run(client, save, interval, record_time, save_directory, csv)


main.add_command(interop_clients.cli_odlc.main, "odlc")


try:
    import interop_clients.geo.cli

    main.add_command(interop_clients.geo.cli.main, "geo")
except ImportError:
    pass

import io
import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import click
from PIL import Image  # type: ignore

from interop_clients import InteropClient, api


def update_odlc(
    client: InteropClient, odlc_path: Path, image_path: Optional[Path],
) -> None:
    with odlc_path.open() as f:
        odlc = json.load(f)
        odlc_id = odlc["id"]
        client.put_odlc(odlc_id, odlc)
    if image_path is not None:
        client.put_odlc_image(odlc_id, image_path.read_bytes())


def upload_odlc(
    client: InteropClient, odlc_path: Path, image_path: Optional[Path]
) -> None:
    with odlc_path.open() as f:
        odlc_id = client.post_odlc(json.load(f))
    if image_path is not None:
        client.put_odlc_image(odlc_id, image_path.read_bytes())


def odlc_image_pairs(
    directory: Path,
) -> Iterable[Tuple[Path, Optional[Path]]]:
    odlcs: Dict[str, Path] = {}
    images: Dict[str, Path] = {}

    for path in directory.iterdir():
        name = path.stem
        ext = path.suffix.lower()

        if ext == ".json":
            if name in odlcs:
                raise ValueError(
                    f"Duplicate ODLC for {name}: "
                    f"'{odlcs[name]}' and '{path}'"
                )
            odlcs[name] = path
        elif ext in {".png", ".jpg", ".jpeg"}:
            if name in images:
                raise ValueError(
                    f"Duplicate ODLC images for {name}: "
                    f"'{images[name]}' and '{path}'"
                )
            images[name] = path

    for name, odlc_path in odlcs.items():
        yield odlc_path, images.get(name)


@click.group()
def main() -> None:
    """View and modify your ODLCs.
    """


@main.command("update")
@click.option(
    "--directory",
    "-d",
    "dirs",
    type=click.Path(file_okay=False),
    multiple=True,
    help="Directory of ODLCs and thumbnails",
)
@click.option(
    "--with-thumbnail",
    "-w",
    type=(api.Id, click.Path(dir_okay=False), click.Path(dir_okay=False)),
    multiple=True,
    help="ID, JSON file, image thumbnail pairs to upload",
)
@click.option(
    "--no-thumbnail",
    "-n",
    type=(api.Id, click.Path(dir_okay=False)),
    multiple=True,
    help="ID, JSON file pairs to upload",
)
@click.pass_context
def update(
    ctx: click.Context,
    dirs: List[os.PathLike],
    with_thumbnail: List[Tuple[os.PathLike, os.PathLike]],
    no_thumbnail: List[os.PathLike],
) -> None:
    """Update already-existing ODLCs.

    ODLCs are specified using JSON files with the extension '.json' and
    thumbnails can be either PNGs or JPEGs. The JSON file must meet the
    `interop_clients.api.Odlc` specification because the IDs used are from that
    file.

    An ODLC is uploaded for each file in a directory that ends in '.json' and
    if an image ending in '.png', '.jpg', or '.jpeg' is found in the same
    directory with the same name, it is also uploaded for that same image.
    """
    client = ctx.obj
    for d in dirs:
        for odlc_path, image_path in odlc_image_pairs(Path(d)):
            update_odlc(client, odlc_path, image_path)
    for odlc_pathlike, thumbnail_pathlike in with_thumbnail:
        update_odlc(client, Path(odlc_pathlike), Path(thumbnail_pathlike))
    for odlc_pathlike in no_thumbnail:
        update_odlc(client, Path(odlc_pathlike), None)


@main.command("upload")
@click.option(
    "--directory",
    "-d",
    "dirs",
    type=click.Path(file_okay=False),
    multiple=True,
    help="Directory of ODLCs and thumbnails",
)
@click.option(
    "--with-thumbnail",
    "-w",
    type=(click.Path(dir_okay=False), click.Path(dir_okay=False)),
    multiple=True,
    help="JSON file, image thumbnail pairs to upload",
)
@click.option(
    "--no-thumbnail",
    "-n",
    type=click.Path(dir_okay=False),
    multiple=True,
    help="JSON files to upload",
)
@click.pass_context
def upload(
    ctx: click.Context,
    dirs: List[os.PathLike],
    with_thumbnail: List[Tuple[os.PathLike, os.PathLike]],
    no_thumbnail: List[os.PathLike],
) -> None:
    """Upload new ODLCs.

    ODLCs are specified using JSON files with the extension '.json' and
    thumbnails can be either PNGs or JPEGs. The JSON file should meet the
    `interop_clients.api.NewOdlc` specification.

    An ODLC is uploaded for each file in a directory that ends in '.json' and
    if an image ending in '.png', '.jpg', or '.jpeg' is found in the same
    directory with the same name, it is also uploaded for that same image.
    """
    client = ctx.obj
    for d in dirs:
        for odlc_path, image_path in odlc_image_pairs(Path(d)):
            upload_odlc(client, odlc_path, image_path)
    for odlc_pathlike, thumbnail_pathlike in with_thumbnail:
        upload_odlc(client, Path(odlc_pathlike), Path(thumbnail_pathlike))
    for odlc_pathlike in no_thumbnail:
        upload_odlc(client, Path(odlc_pathlike), None)


@main.command("delete")
@click.argument("ids", type=int, nargs=-1)
@click.option(
    "--all", "-a", "delete_all", is_flag=True, help="Delete all your ODLCs"
)
# It's not possible to only delete the info
@click.option(
    "--image", "-i", "image_only", is_flag=True, help="Only delete images"
)
@click.pass_context
def delete(
    ctx: click.Context, ids: List[int], delete_all: bool, image_only: bool
) -> None:
    """Delete ODLCs by ID.
    """
    client = ctx.obj
    delete = client.delete_odlc_image if image_only else client.delete_odlc
    if delete_all:
        for odlc in client.get_odlcs():
            delete(odlc["id"])
    else:
        for odlc_id in ids:
            delete(odlc_id)


@main.command("info")
@click.pass_context
def info(ctx: click.Context) -> None:
    """Show human-readable info about your ODLCs.
    """
    client = ctx.obj
    odlcs = client.get_odlcs()
    click.echo(json.dumps(odlcs, indent=4, sort_keys=True))


@main.command("dump")
@click.argument(
    "output_dir",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    default=".",
)
@click.option(
    "--info/--no-info",
    default=True,
    help="Whether to save ODLC information into JSON files (default: --info)",
)
@click.option(
    "--images/--no-images",
    default=True,
    help="Whether to download and save ODLC thumbnails (default: --images)",
)
@click.option(
    "--pretty/--no-pretty",
    default=False,
    help="Whether to format the ODLC JSON files (default: --no-pretty)",
)
@click.pass_context
def dump(
    ctx: click.Context,
    output_dir: os.PathLike,
    info: bool,
    images: bool,
    pretty: bool,
) -> None:
    """Download Interop's ODLCs and images.
    """
    client = ctx.obj

    # Optimization for when we don't have to do anything
    if not info and not images:
        return

    directory = Path(output_dir)

    # We know that directory either doesn't exist or is a writable directory by
    # the guarantees of click.Path
    if not directory.exists():
        directory.mkdir()

    for odlc in client.get_odlcs():
        odlc_id = odlc["id"]

        if info:
            info_path = directory / f"{odlc_id}.json"
            with info_path.open("w") as fodlc:
                if pretty:
                    json.dump(odlc, fodlc, indent=4, sort_keys=True)
                else:
                    json.dump(odlc, fodlc)

        if images:
            img_bytes = client.get_odlc_image(odlc_id)
            with Image.open(io.BytesIO(img_bytes)) as img:
                img_path = directory / f"{odlc_id}.{img.format.lower()}"
                img.save(img_path)

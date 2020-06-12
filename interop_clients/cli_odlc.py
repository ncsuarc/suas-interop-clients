import io
import json
import os
import pprint
from pathlib import Path
from typing import IO, Dict, Iterable, List, Optional, Tuple

import click
from PIL import Image  # type: ignore

from interop_clients import InteropClient, api


def update_odlc(
    client: InteropClient,
    odlc_id: api.Id,
    odlc_path: Path,
    image_path: Optional[Path],
) -> None:
    with odlc_path.open() as f:
        client.put_odlc(odlc_id, json.load(f))
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
) -> Iterable[Tuple[str, Path, Optional[Path]]]:
    odlcs: Dict[str, Path] = {}
    images: Dict[str, Path] = {}

    for path in directory.iterdir():
        name = path.stem
        ext = path.suffix

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
        yield name, odlc_path, images.get(name)


def update_dir(client: InteropClient, directory: Path) -> None:
    for name, odlc_path, image_path in odlc_image_pairs(directory):
        odlc_id = api.Id(name)
        update_odlc(client, odlc_id, odlc_path, image_path)


def upload_dir(client: InteropClient, directory: Path) -> None:
    for _name, odlc_path, image_path in odlc_image_pairs(directory):
        upload_odlc(client, odlc_path, image_path)


@click.group()
def main() -> None:
    """ODLC subcommand.
    """


@main.command("update")
@click.option("--directory", "-d", "dirs", multiple=True)
@click.option(
    "--with-thumbnail",
    "-w",
    type=(api.Id, click.Path(dir_okay=False), click.Path(dir_okay=False)),
    multiple=True,
)
@click.option(
    "--no-thumbnail",
    "-n",
    type=(api.Id, click.Path(dir_okay=False)),
    multiple=True,
)
@click.pass_context
def update(
    ctx: click.Context,
    dirs: List[os.PathLike],
    with_thumbnail: List[Tuple[api.Id, os.PathLike, os.PathLike]],
    no_thumbnail: List[Tuple[api.Id, os.PathLike]],
) -> None:
    client = ctx.obj
    for d in dirs:
        update_dir(client, Path(d))
    for odlc_id, odlc_path, thumbnail_path in with_thumbnail:
        update_odlc(client, odlc_id, Path(odlc_path), Path(thumbnail_path))
    for odlc_id, odlc_path in no_thumbnail:
        update_odlc(client, odlc_id, Path(odlc_path), None)


@main.command("upload")
@click.option("--directory", "-d", "dirs", multiple=True)
@click.option(
    "--with-thumbnail",
    "-w",
    type=(click.Path(dir_okay=False), click.Path(dir_okay=False)),
    multiple=True,
)
@click.option(
    "--no-thumbnail", "-n", type=click.Path(dir_okay=False), multiple=True
)
@click.pass_context
def upload(
    ctx: click.Context,
    dirs: List[str],
    with_thumbnail: List[Tuple[os.PathLike, os.PathLike]],
    no_thumbnail: List[os.PathLike],
) -> None:
    client = ctx.obj
    for d in dirs:
        upload_dir(client, Path(d))
    for odlc_path, thumbnail_path in with_thumbnail:
        upload_odlc(client, Path(odlc_path), Path(thumbnail_path))
    for odlc_path in no_thumbnail:
        upload_odlc(client, Path(odlc_path), None)


@main.command("delete")
@click.argument("ids", type=int, nargs=-1)
@click.option("--all", "-a", "delete_all", is_flag=True)
# It's not possible to only delete the info
@click.option("--image", "-i", "image_only", is_flag=True)
@click.pass_context
def delete(
    ctx: click.Context, ids: List[int], delete_all: bool, image_only: bool
) -> None:
    client = ctx.obj
    delete = client.delete_odlc_image if image_only else client.delete_odlc
    if delete_all:
        for odlc in client.get_odlcs():
            delete(odlc["id"])
    else:
        for odlc_id in ids:
            delete(odlc_id)


@main.command("info")
@click.option(
    "--output", "-o", type=click.File("w"),
)
@click.option("--minify", is_flag=True)
@click.pass_context
def info(ctx: click.Context, output: IO[str], minify: bool) -> None:
    client = ctx.obj
    if minify:
        print(client.get_odlcs(), file=output)
    else:
        pprint.pprint(client.get_odlcs(), stream=output)


@main.command("dump")
@click.argument(
    "output_dir",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    default=".",
)
@click.option("--info/--no-info", default=True)
@click.option("--images/--no-images", default=True)
@click.option("--pretty/--no-pretty", default=False)
@click.pass_context
def dump(
    ctx: click.Context,
    output_dir: os.PathLike,
    info: bool,
    images: bool,
    pretty: bool,
) -> None:
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
                    pprint.pprint(odlc, stream=fodlc)
                else:
                    print(odlc, file=fodlc)

        if images:
            img_bytes = client.get_odlc_image(odlc_id)
            with Image.open(io.BytesIO(img_bytes)) as img:
                img_path = directory / f"{odlc_id}.{img.format.lower()}"
                img.save(img_path)

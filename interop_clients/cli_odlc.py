import json
import os
import pprint
from typing import Dict, Iterable, List, Optional, Tuple

import click

from interop_clients import InteropClient, api


def update_odlc(
    io: InteropClient,
    odlc_id: api.Id,
    odlc_path: str,
    image_path: Optional[str],
) -> None:
    with open(odlc_path) as f:
        io.put_odlc(odlc_id, json.load(f))
    if image_path is not None:
        with open(image_path, "rb") as img:
            io.put_odlc_image(odlc_id, img.read())


def upload_odlc(
    io: InteropClient, odlc_path: str, image_path: Optional[str]
) -> None:
    with open(odlc_path) as f:
        odlc_id = io.post_odlc(json.load(f))
    if image_path is not None:
        with open(image_path, "rb") as img:
            io.put_odlc_image(odlc_id, img.read())


def odlc_image_pairs(
    directory: str,
) -> Iterable[Tuple[str, str, Optional[str]]]:
    odlcs: Dict[str, str] = {}
    images: Dict[str, str] = {}

    with os.scandir(directory) as it:
        for entry in it:
            name, ext = os.path.splitext(entry.name)
            ext = ext.lower()

            if ext == ".json":
                if name in odlcs:
                    raise ValueError(
                        f"Duplicate ODLC files for {repr(name)}: "
                        f"{repr(odlcs[name])} and {repr(entry.path)}"
                    )
                odlcs[name] = entry.path
            elif ext in {".png", ".jpg", ".jpeg"}:
                if name in images:
                    raise ValueError(
                        f"Duplicate ODLC images for {repr(name)}: "
                        f"{repr(images[name])} and {repr(entry.path)}"
                    )
                images[name] = entry.path

    for name, odlc_path in odlcs.items():
        yield name, odlc_path, images.get(name)


def update_dir(io: InteropClient, directory: str) -> None:
    for name, odlc_path, image_path in odlc_image_pairs(directory):
        odlc_id = api.Id(name)
        update_odlc(io, odlc_id, odlc_path, image_path)


def upload_dir(io: InteropClient, directory: str) -> None:
    for _name, odlc_path, image_path in odlc_image_pairs(directory):
        upload_odlc(io, odlc_path, image_path)


@click.group()
def main() -> None:
    """ODLC subcommand.
    """


@main.command("update")
@click.option("--directory", "-d", "dirs", multiple=True)
@click.option("--with-thumbnail", "-w", type=(api.Id, str, str), multiple=True)
@click.option("--no-thumbnail", "-n", type=(api.Id, str), multiple=True)
@click.pass_context
def update(
    ctx: click.Context,
    dirs: List[str],
    with_thumbnail: List[Tuple[api.Id, str, str]],
    no_thumbnail: List[Tuple[api.Id, str]],
) -> None:
    io = ctx.obj
    for d in dirs:
        update_dir(io, d)
    for odlc_id, odlc_path, thumbnail_path in with_thumbnail:
        update_odlc(io, odlc_id, odlc_path, thumbnail_path)
    for odlc_id, odlc_path in no_thumbnail:
        update_odlc(io, odlc_id, odlc_path, None)


@main.command("upload")
@click.option("--directory", "-d", "dirs", multiple=True)
@click.option("--with-thumbnail", "-w", type=(str, str), multiple=True)
@click.option("--no-thumbnail", "-n", type=str, multiple=True)
@click.pass_context
def upload(
    ctx: click.Context,
    dirs: List[str],
    with_thumbnail: List[Tuple[str, str]],
    no_thumbnail: List[str],
) -> None:
    io = ctx.obj
    for d in dirs:
        upload_dir(io, d)
    for odlc_path, thumbnail_path in with_thumbnail:
        upload_odlc(io, odlc_path, thumbnail_path)
    for odlc_path in no_thumbnail:
        upload_odlc(io, odlc_path, None)


@main.command("delete")
@click.argument("ids", type=int, nargs=-1)
@click.option("--all", "-a", "delete_all", is_flag=True)
@click.option("--image", "-i", "image_only", is_flag=True)
@click.pass_context
def delete(
    ctx: click.Context, ids: List[int], delete_all: bool, image_only: bool
) -> None:
    io = ctx.obj
    delete = io.delete_odlc_image if image_only else io.delete_odlc
    if delete_all:
        for odlc in io.get_odlcs():
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
def info(ctx: click.Context, output: click.File, minify: bool) -> None:
    io = ctx.obj
    if minify:
        print(io.get_odlcs(), file=output)
    else:
        pprint.pprint(io.get_odlcs(), stream=output)


# TODO: Add options to output to file(s)
@main.command("dump")
@click.option(
    "--directory", "-d", type=click.Path(writable=True), default=".",
)
# TODO: Use PIL to automatically determine the extension
@click.option("--image-extension", "-e", required=True)
@click.option("--pretty", "-p", is_flag=True)
@click.pass_context
def dump(
    ctx: click.Context,
    directory: os.PathLike,
    image_extension: str,
    pretty: bool,
) -> None:
    io = ctx.obj

    for odlc in io.get_odlcs():
        odlc_id = odlc["id"]
        with open(os.path.join(directory, f"{odlc_id}.json"), "w") as fodlc:
            if pretty:
                pprint.pprint(io.get_odlcs(), stream=fodlc)
            else:
                print(io.get_odlcs(), file=fodlc)
        with open(
            os.path.join(directory, f"{odlc_id}.{image_extension}"), "wb"
        ) as fimage:
            fimage.write(io.get_odlc_image(odlc_id))

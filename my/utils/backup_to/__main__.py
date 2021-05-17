"""
Helper script to locate a directory to backup to
while on an operating system (computer vs. phone)

Typically this backs up to ~/data/dirname on my computer
~/data/phone/dirname on my phone
"""

import shutil
from os import environ, path
from pathlib import Path

import click

# if the HPIDATA environment variable is set (which points to my data)
# use that. Else, just default to ~/data
BASE_PREFIX: Path = Path(environ.get("HPIDATA", path.join(environ["HOME"], "data")))


def _on_android() -> bool:
    return shutil.which("termux-setup-storage") is not None


@click.command()
@click.argument("NAME")
def main(name: str) -> None:
    base: Path
    if _on_android():
        base = BASE_PREFIX / "phone"
    else:
        base = BASE_PREFIX
    to = (base / name).absolute()
    to.mkdir(parents=True, exist_ok=True)
    click.echo(str(to))


if __name__ == "__main__":
    main(prog_name="backup_dir")
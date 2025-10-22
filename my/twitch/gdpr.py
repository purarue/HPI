"""
Parses the twitch GDPR data request
https://www.twitch.tv/p/en/legal/privacy-choices/#user-privacy-requests
"""

# see https://github.com/purarue/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import twitch as user_config  # type: ignore[attr-defined]

from dataclasses import dataclass
from my.core import PathIsh


@dataclass
class config(user_config.gdpr):
    gdpr_dir: PathIsh  # path to unpacked GDPR archive


import csv
from datetime import datetime
from pathlib import Path
from collections.abc import Iterator, Sequence

from .common import Event, Results

from my.core import make_logger
from my.core.cachew import mcachew
from my.core.common import get_files

logger = make_logger(__name__)


def inputs() -> Sequence[Path]:
    return get_files(config.gdpr_dir, glob="*.csv")


def _cachew_depends_on() -> list[float]:
    return [p.stat().st_mtime for p in inputs()]


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def events() -> Results:
    for file in inputs():
        yield from _parse_csv_file(file)


def _parse_csv_file(p: Path) -> Iterator[Event]:
    with p.open("r") as f:
        reader = csv.reader(f)
        next(reader)  # ignore header
        for line in reader:
            context: str | int
            context = line[6]
            if context.isdigit():
                context = int(line[6])
            yield Event(
                event_type=line[0],
                dt=datetime.fromisoformat(line[1]),
                channel=line[5],
                context=context,
            )

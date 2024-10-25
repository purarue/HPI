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
from typing import Iterator, Union, Sequence, List

from .common import Event, Results

from my.core import make_logger
from my.core.cachew import mcachew
from my.core.common import get_files
from my.utils.input_source import InputSource

logger = make_logger(__name__)


def inputs() -> Sequence[Path]:
    return get_files(config.gdpr_dir, glob="*.csv")


def _cachew_depends_on(for_paths: InputSource = inputs) -> List[float]:
    return [p.stat().st_mtime for p in for_paths()]


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def events(from_paths: InputSource = inputs) -> Results:
    for file in from_paths():
        yield from _parse_csv_file(file)


def _parse_csv_file(p: Path) -> Iterator[Event]:
    with p.open("r") as f:
        reader = csv.reader(f)
        next(reader)  # ignore header
        for line in reader:
            context: Union[str, int]
            context = line[6]
            if context.isdigit():
                context = int(line[6])
            yield Event(
                event_type=line[0],
                dt=datetime.fromisoformat(line[1]),
                channel=line[5],
                context=context,
            )

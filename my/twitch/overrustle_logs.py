"""
Reads parsed information from the overrustle logs dump
https://github.com/purarue/overrustle_parser
"""

# see https://github.com/purarue/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import twitch as user_config  # type: ignore[attr-defined]

from dataclasses import dataclass
from my.core import Paths


@dataclass
class config(user_config.overrustle):
    export_path: Paths  # parsed overrustle_parser json files


import json
from pathlib import Path
from typing import Sequence, List

from my.core import make_logger
from my.core.cachew import mcachew
from my.core.common import get_files
from my.utils.time import parse_datetime_sec

from .common import Event, Results

logger = make_logger(__name__)


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


def _cachew_depends_on() -> List[float]:
    return [p.stat().st_mtime for p in inputs()]


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def events() -> Results:
    for file in inputs():
        yield from _parse_json_dump(file)


def _parse_json_dump(p: Path) -> Results:
    for blob in json.loads(p.read_text()):
        yield Event(
            event_type="chatlog",
            dt=parse_datetime_sec(blob["dt"]),
            channel=blob["channel"],
            context=blob["message"],
        )

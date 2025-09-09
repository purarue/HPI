"""
Parses generic event data from my parsed GDPR data
from: https://github.com/purarue/blizzard_gdpr_parser
"""

# see https://github.com/purarue/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import blizzard as user_config  # type: ignore[attr-defined]
from dataclasses import dataclass
from my.core import PathIsh, make_logger
from my.core.cachew import mcachew


@dataclass
class config(user_config.gdpr):
    # path to the exported data
    export_path: PathIsh


import json
from pathlib import Path
from datetime import datetime
from typing import NamedTuple
from collections.abc import Iterator, Sequence
from itertools import chain

from my.core import get_files, Stats
from my.utils.time import parse_datetime_sec


logger = make_logger(__name__)


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


def _cachew_depends_on() -> list[float]:
    return [p.stat().st_mtime for p in inputs()]


class Event(NamedTuple):
    dt: datetime
    event_tag: str
    metadata: list[str]


Results = Iterator[Event]


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def events() -> Results:
    yield from chain(*map(_parse_json_file, inputs()))


def _parse_json_file(p: Path) -> Results:
    for e_info in json.loads(p.read_text()):
        dt, meta_tuple = e_info
        meta_tag, meta_joined = meta_tuple
        yield Event(
            dt=parse_datetime_sec(dt),
            event_tag=meta_tag,
            metadata=meta_joined.split("|"),
        )


def stats() -> Stats:
    from my.core import stat

    return {**stat(events)}

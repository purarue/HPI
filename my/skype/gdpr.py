"""
Parse Message Dates from Skypes GDPR JSON export
"""

REQUIRES = ["dateparser"]

# Isn't a lot of data here, seems a lot of the old
# data is gone. Only parses a couple messages, might
# as well use the datetimes for context on when I
# was using skype

# see https://github.com/purarue/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import skype as user_config  # type: ignore[attr-defined]

from dataclasses import dataclass
from my.core import Paths, Stats


@dataclass
class config(user_config.gdpr):
    # path[s]/glob to the skype JSON files
    export_path: Paths


import json
from pathlib import Path
from datetime import datetime
from typing import Iterator, Sequence
from itertools import chain

import dateparser

from my.core import get_files, make_logger
from my.utils.input_source import InputSource

logger = make_logger(__name__)


Results = Iterator[datetime]


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


def timestamps(from_paths: InputSource = inputs) -> Results:
    yield from chain(*map(_parse_file, from_paths()))


def _parse_file(post_file: Path) -> Results:
    items = json.loads(post_file.read_text())
    for conv in items["conversations"]:
        for msg in conv["MessageList"]:
            d = dateparser.parse(msg["originalarrivaltime"].rstrip("Z"))
            if d is not None:
                yield d


def stats() -> Stats:
    from my.core import stat

    return {**stat(timestamps)}

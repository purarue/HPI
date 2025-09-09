"""
Parses chess games from chess.com/lichess.org using
https://github.com/purarue/chess_export
"""

REQUIRES = ["git+https://github.com/purarue/chess_export"]

# see https://github.com/purarue/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import chess as user_config  # type: ignore[attr-defined]


from pathlib import Path
from typing import Union
from collections.abc import Iterator, Sequence
from itertools import chain

import chess_export.chessdotcom.model as cmodel
import chess_export.lichess.model as lmodel
from more_itertools import unique_everseen

from dataclasses import dataclass
from my.core import get_files, Stats, make_logger, Paths
from my.core.cachew import mcachew


@dataclass
class config(user_config.export):
    # path[s]/glob to the exported data. These are the resulting JSON files from 'chess_export ... export'
    export_path: Paths


logger = make_logger(__name__)


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


# TODO: make extendible? Not sure if anyone has any other things they need to include here though...
Results = Iterator[Union[cmodel.ChessDotComGame, lmodel.LichessGame]]


def _cachew_depends_on() -> list[float]:
    return [p.stat().st_mtime for p in inputs()]


def _parse_export_file(p: Path) -> Results:
    # try one, else the other
    # typically this raises a KeyError since the JSON didn't match
    # what the NamedTuple expects
    try:
        yield from lmodel.from_export(p)
    except Exception:
        yield from cmodel.from_export(p)


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def history() -> Results:
    yield from unique_everseen(
        chain(*(_parse_export_file(p) for p in inputs())), key=lambda g: g.end_time
    )


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}

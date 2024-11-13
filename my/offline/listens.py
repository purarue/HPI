"""
Parses scrobbles from https://github.com/purarue/offline_listens
"""

REQUIRES = ["git+https://github.com/purarue/offline_listens"]

# see https://github.com/purarue/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import offline as user_config  # type: ignore[attr-defined]


from pathlib import Path
from typing import Iterator, Sequence

from offline_listens.listens import Listen
from offline_listens.parse import iter_dir, parse_file

from dataclasses import dataclass
from my.core import get_files, Stats, Paths


@dataclass
class config(user_config.listens):
    # path[s]/glob to the exported data
    export_path: Paths


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


Results = Iterator[Listen]


def history() -> Results:
    for f in inputs():
        if f.is_dir():
            yield from iter_dir(f)
        else:
            yield from parse_file(f)


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}

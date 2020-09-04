"""
Manually Scraped Forum Posts from Random Forums I've used in the past
https://github.com/seanbreckenridge/forum_parser
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import old_forums as user_config  # type: ignore

from dataclasses import dataclass

from .core import Paths


@dataclass
class old_forums(user_config):
    # path[s]/glob to the parsed JSON files
    export_path: Paths


from .core.cfg import make_config
config = make_config(old_forums)

#######

import json
from pathlib import Path
from typing import Sequence

from .core import get_files


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


from datetime import datetime, timezone
from typing import NamedTuple, Iterable
from itertools import chain

from .core.common import LazyLogger
logger = LazyLogger(__name__)

# represents one post on a forum entry
class Post(NamedTuple):
    dt: datetime
    post_title: str
    post_url: str
    post_contents: str  # eh, doesnt match contents, whatever
    forum_name: str


Results = Iterable[Post]


def history(from_paths=inputs) -> Results:
    yield from chain(*map(_parse_file, from_paths()))


def _parse_file(post_file: Path) -> Results:
    with post_file.open('r') as pf:
        items = json.load(pf)
    for p in items:
        yield Post(
            dt=datetime.fromtimestamp(p["date"], tz=timezone.utc),
            post_title=p["post_title"],
            post_url=p["post_url"],
            post_contents=p["contents"],
            forum_name=p["forum_name"],
        )


def stats():
    from .core import stat
    return {
        **stat(history)
    }
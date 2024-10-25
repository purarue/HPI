"""
Any Media being played on my computer with mpv
Uses my mpv-history-daemon
https://github.com/purarue/mpv-history-daemon
"""

REQUIRES = ["git+https://github.com/purarue/mpv-history-daemon"]

# see https://github.com/purarue/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import mpv as user_config  # type: ignore[attr-defined]

from typing import Iterator, Sequence, Optional
from dataclasses import dataclass
from my.core import Paths, make_config


@dataclass
class mpv_config(user_config.history_daemon):
    # glob to the JSON files that the daemon writes whenever Im using mpv
    export_path: Paths

    # amount of song I should have listened to to qualify it as a listen (e.g. 0.5, 0.75)
    require_percent: Optional[float] = None


config = make_config(mpv_config)


import itertools
from pathlib import Path

from mpv_history_daemon.events import (
    Media,
    all_history as M_all_history,
    _actually_listened_to,
)

from my.core import get_files, Stats, make_logger
from my.utils.input_source import InputSource


logger = make_logger(__name__)

# monkey patch logs
import mpv_history_daemon.events

mpv_history_daemon.events.logger = mpv_history_daemon.events.setup_logger(
    name="mpv_history_events", level=logger.level
)

Results = Iterator[Media]


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(history),
    }


def inputs() -> Sequence[Path]:
    # this takes the files, sorts it so merged event files
    # are returned first, then the individual event ones
    # this makes it so that history is close to (it may not be if you opened 2 mpv
    # instances and listened to something while another was paused) chronologically sorted,
    # because the merged files are ordered by keyname
    files = list(get_files(config.export_path, sort=True))
    groups = {
        k: list(g)
        for k, g in itertools.groupby(files, key=lambda f: "merged" in f.stem)
    }
    # merged files, then raw event files
    return list(itertools.chain(groups.get(True, []), groups.get(False, [])))


def _filter_by(m: Media) -> bool:
    if m.is_stream:
        return True
    # if duration is under 10 minutes, but listen_time is over
    # 3 hours, probably a broken item, caused by hanging mpv/socket?
    # I only have 2 of these, in the 13,000 or so history items
    if m.media_duration is not None and m.media_duration < 600:
        if m.listen_time > 10800:
            logger.debug(f"Assuming this is a broken file: {str(m)}")
            return False
    perc = config.require_percent or 0.75
    # fallback to library func
    return _actually_listened_to(m, require_listened_to_percent=perc)


def all_history(from_paths: InputSource = inputs) -> Results:
    yield from M_all_history(list(from_paths()))


def history(from_paths: InputSource = inputs) -> Results:
    yield from filter(_filter_by, all_history(from_paths))

"""
When I completed https://projecteuler.net problems

This information has to be updated manually, I do it once
every few months/years depending on how many of these I keep
solving

To download, log in to your Project Euler account
(in your browser), and then go to:
https://projecteuler.net/history

That txt file is what this accepts as input (can accept multiple)
"""

# see https://github.com/purarue/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import project_euler as user_config  # type: ignore[attr-defined]

from dataclasses import dataclass
from my.core import Paths


@dataclass
class config(user_config):
    # path[s]/glob to the .txt export files
    export_path: Paths


import re
import csv
from pathlib import Path
from datetime import datetime, timezone
from typing import Sequence, Iterator, NamedTuple, Optional, List, Dict
from itertools import chain, groupby

from my.core import get_files, Stats
from my.utils.input_source import InputSource


class Solution(NamedTuple):
    problem: int
    dt: datetime
    name: Optional[str]


def project_euler_inputs() -> Sequence[Path]:
    return get_files(config.export_path)


def history(from_paths: InputSource = project_euler_inputs) -> Iterator[Solution]:
    # need to sort here to dedupe accurately
    items: List[Solution] = sorted(
        chain(*map(_parse_file, from_paths())), key=lambda s: s.problem
    )
    # group by items, and if there are multiple return the one with the name
    # (or None if there is no name)
    grouped: Dict[int, List[Solution]] = {
        num: list(problems) for num, problems in groupby(items, lambda s: s.problem)
    }
    for items in grouped.values():
        for item in items:
            if item.name is not None:
                yield item
                break  # break out of the inner loop
        else:
            # no name on item, just yield the first
            yield items[0]


# Example line:
# 037: 07 Nov 14 (13:46)
# project euler was started in early 2000s,
# so no need to support 19XX
# '14' means 2014
OLD_LINE_REGEX = re.compile(r"(\d+):\s*(\d+)\s*(\w+)\s*(\d+)\s*\((\d+):(\d+)\)")

# hardcoding instead of using calendar module avoid possible issues with locale
MONTHS = [
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
]


def _parse_file(p: Path) -> Iterator[Solution]:
    for line in p.open():
        m = OLD_LINE_REGEX.match(line)
        if m:
            # old format
            problem, day, month_desc, year_short, hour, minute = m.groups()
            month_lowered = month_desc.lower()
            assert month_lowered in MONTHS, f"Couldn't find {month_lowered} in {MONTHS}"
            # datetimes in the file are UTC time
            yield Solution(
                problem=int(problem),
                dt=datetime(
                    year=int(f"20{year_short}"),
                    month=MONTHS.index(month_lowered) + 1,
                    day=int(day),
                    hour=int(hour),
                    minute=int(minute),
                    tzinfo=timezone.utc,
                ),
                name=None,
            )
        else:
            # new format
            csv_reader = csv.reader([line])
            row = next(csv_reader)
            dt = datetime.strptime(row[0], "%d %b %y (%H:%M)")
            yield Solution(problem=int(row[1]), dt=dt, name=row[2])


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}

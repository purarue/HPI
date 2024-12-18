"""
Parses steam game/achievement data scraped with
https://github.com/purarue/steamscraper
"""

# see https://github.com/purarue/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import steam as user_config  # type: ignore[attr-defined]
from dataclasses import dataclass
from my.core import Paths


@dataclass
class config(user_config.scraper):
    # path to the exported data
    export_path: Paths


import json
from functools import partial
from pathlib import Path
from datetime import datetime
from typing import NamedTuple, Iterator, Sequence, Dict, List, Optional, Any
from itertools import groupby

from my.core import get_files, Stats, Res
from my.utils.time import parse_datetime_sec


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


class Achievement(NamedTuple):
    title: str
    description: str
    achieved: bool
    game_name: str
    achieved_on: Optional[datetime]
    icon: Optional[str]


class Game(NamedTuple):
    id: int
    name: str
    hours_played: float
    achievements: List[Achievement]
    image_url: Optional[str]

    @property
    def achieved(self) -> int:
        return list(map(lambda g: g.achieved, self.achievements)).count(True)

    @property
    def achievement_count(self) -> int:
        return len(self.achievements)

    @property
    def achievement_percentage(self) -> float:
        return self.achieved / self.achievement_count


Results = Iterator[Res[Game]]
AchievementResults = Iterator[Res[Achievement]]


def games() -> Results:
    """only ones I've played"""
    for game in all_games():
        if isinstance(game, Exception):
            yield game
        else:
            if game.hours_played > 0.0:
                yield game


def all_games() -> Results:
    # combine the results from multiple files
    games_no_exc: List[Game] = []
    for json_file in inputs():
        for g in _read_parsed_json(json_file):
            if isinstance(g, Exception):
                yield g
            else:
                assert isinstance(g, Game)
                games_no_exc.append(g)

    # only return the single game with the most achievement count if there are duplicates
    for _, gm in groupby(sorted(games_no_exc, key=lambda x: x.id), lambda x: x.id):
        yield max(gm, key=lambda gmo: gmo.achieved)


def all_achievements() -> AchievementResults:
    # combine the results from multiple achievement lists
    for game in all_games():
        if isinstance(game, Exception):
            yield game
        else:
            yield from game.achievements


# only ones which Ive actually achieved
def achievements() -> AchievementResults:
    for ach in all_achievements():
        if isinstance(ach, Exception):
            yield ach
        else:
            if ach.achieved:
                yield ach


def _read_parsed_json(p: Path) -> Results:
    items = json.loads(p.read_text())
    for _, game in items.items():
        ach_lambda = partial(_parse_achievement, game_name=game["name"])
        try:
            yield Game(
                id=game["id"],
                name=game["name"],
                hours_played=game["hours"],
                image_url=game["image"],
                achievements=list(map(ach_lambda, game["achievements"])),
            )
        except TypeError as e:
            # error creating datetime?
            yield e


def _parse_achievement(ach: Dict[str, Any], game_name: str) -> Achievement:
    achieved = ach["progress"]["unlocked"]
    achieved_on = None
    # parse datetime if it has it
    # could possibly throw an error, but its caught above
    if achieved:
        achieved_on = parse_datetime_sec(ach["progress"]["data"])
    return Achievement(
        title=ach["title"],
        description=ach["description"],
        game_name=game_name,
        achieved=achieved,
        achieved_on=achieved_on,
        icon=ach.get("icon"),
    )


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(games),
        **stat(achievements),
    }

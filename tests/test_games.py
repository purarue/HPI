from typing import List

from more_itertools import ilen
from my.core.error import raise_exceptions

from .common import skip_if_not_pura


@skip_if_not_pura
def test_league() -> None:
    from my.league.export import history, Game

    gs: List[Game] = list(raise_exceptions(history()))
    assert len(gs) > 50


@skip_if_not_pura
def test_steam() -> None:
    from my.steam.scraper import games, achievements, Achievement

    assert ilen(games()) > 10
    ach: List[Achievement] = list(raise_exceptions(achievements()))
    assert any([a.game_name == "Counter-Strike: Global Offensive" for a in ach])

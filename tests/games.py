from more_itertools import ilen

def test_blizzard():
    from my.games.blizzard import events
    ev = list(events())
    assert len(ev) >= 100

def test_league():
    from my.games.league import history
    gs = list(history())
    assert len(gs) > 50
    assert len(gs[0].players) == 10

def test_steam():
    from my.games.steam import games, achievements
    assert ilen(games()) > 10
    ach = list(achievements())
    assert any([a.game_name == "Counter-Strike: Global Offensive" for a in ach])

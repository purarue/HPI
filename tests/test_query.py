from datetime import timedelta

import pytest

from my.zsh import history
from my.core.query import find_hpi_function, QueryException, most_recent


def test_query_succeeds():
    assert hasattr(next(find_hpi_function("my.zsh", "history")()), "command")


def test_query_fails():
    with pytest.raises(QueryException):
        find_hpi_function("my.zshh", "history")
    with pytest.raises(QueryException):
        find_hpi_function("my.zsh", "historyy")


def test_get_recent():
    zsh_hist = find_hpi_function("my.zsh", "history")

    recent_events = list(most_recent(zsh_hist(), events=100))
    assert len(recent_events) == 100

    recent_events = list(most_recent(zsh_hist(), events=5))
    assert len(recent_events) == 5

    recent_events = list(most_recent(zsh_hist(), time_range=timedelta(days=10000)))
    assert len(recent_events) == 250

    # find most recent zsh history event 'manually'
    manual_most_recent = sorted(history(), key=lambda o: o.dt)[-1]

    # make sure 'most_recent' function returns the right info
    assert int(manual_most_recent.dt.timestamp()) == int(
        recent_events[0].dt.timestamp()
    )
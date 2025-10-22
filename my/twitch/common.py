from datetime import datetime
from typing import NamedTuple
from collections.abc import Iterator

from my.core import __NOT_HPI_MODULE__  # noqa: F401


class Event(NamedTuple):
    event_type: str
    dt: datetime
    channel: str
    # e.g., additional data/chatlog message
    context: str | int


Results = Iterator[Event]

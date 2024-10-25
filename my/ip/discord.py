from typing import Iterator

from my.ip.common import IP, drop_private  # type: ignore[import]


from my.core import make_logger, Stats
from my.core.cachew import mcachew
from my.core.source import import_source

logger = make_logger(__name__)


@import_source(module_name="my.discord.data_export")
def ips() -> Iterator[IP]:
    from my.discord.data_export import activity, _cachew_depends_on

    @mcachew(depends_on=_cachew_depends_on, logger=logger)
    def _discord_ips() -> Iterator[IP]:
        for a in activity():
            if a.fingerprint.ip is not None:
                yield IP(dt=a.timestamp, addr=a.fingerprint.ip)

    yield from drop_private(_discord_ips())


def stats() -> Stats:
    from my.core import stat

    return {**stat(ips)}

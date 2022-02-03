"""
Discord Data: messages and events data
"""
REQUIRES = [
    "git+https://github.com/seanbreckenridge/discord_data",
    "urlextract",
]


from typing import List

from my.config import discord as user_config  # type: ignore[attr-defined]
from my.core import PathIsh, dataclass


@dataclass
class config(user_config.data_export):

    # path to the top level discord export directory
    # see https://github.com/seanbreckenridge/discord_data for more info
    export_path: PathIsh


from typing import Iterator, Optional, Tuple, Set
from my.core.common import LazyLogger, Stats, mcachew, get_files
from my.core.structure import match_structure

from discord_data import parse_messages, parse_activity, Activity, Message
from urlextract import URLExtract  # type: ignore[import]


logger = LazyLogger(__name__, level="warning")


def _remove_suppression(text: str, first_index: int, second_index: int) -> str:
    # add spaces so that text like <link1><link2>
    # don't get converted into one long link
    return (
        text[:first_index]  # before URL
        + " "
        + text[first_index + 1 : second_index]  # URL itself
        + " "
        + text[second_index + 1 :]  # after URL
    )


extractor = URLExtract()


def _remove_link_suppression(
    content: str, urls: Optional[List[Tuple[str, Tuple[int, int]]]] = None
) -> str:
    # fix content to remove discord link suppression if any links had any
    # e.g. this is a suppressed link <https://github.com>

    if urls is None:
        urls = extractor.find_urls(content, get_indices=True)

    for (url_text, (start_index, end_index)) in urls:
        before_ind = start_index - 1
        after_ind = end_index
        try:
            if content[before_ind] == "<" and content[after_ind] == ">":
                content = _remove_suppression(content, before_ind, after_ind)
        except IndexError:  # could happen if the url didn't have braces and we hit the end of a string
            continue
    return content.strip()


def test_remove_link_suppression() -> None:
    content = "<test>"
    l = content.index("<")
    r = content.index(">")
    assert _remove_suppression(content, l, r) == " test "

    # shouldn't affect this at all
    content = "https://urlextract.readthedocs.io"
    assert _remove_link_suppression(content) == content

    content = "<https://urlextract.readthedocs.io>"
    expected = content.strip("<").strip(">")
    assert _remove_link_suppression(content) == expected

    content = "Here is some text <https://urlextract.readthedocs.io>"
    expected = "Here is some text  https://urlextract.readthedocs.io"
    assert _remove_link_suppression(content) == expected

    content = "text <https://urlextract.readthedocs.io> other text"
    expected = "text  https://urlextract.readthedocs.io  other text"
    assert _remove_link_suppression(content) == expected

    content = "t <https://urlextract.readthedocs.io> other <github.com> f <sean.fish>"
    expected = "t  https://urlextract.readthedocs.io  other  github.com  f  sean.fish"
    assert _remove_link_suppression(content) == expected

    content = "t <https://urlextract.readthedocs.io><sean.fish>"
    expected = "t  https://urlextract.readthedocs.io  sean.fish"
    assert _remove_link_suppression(content) == expected


def _cachew_depends_on() -> List[str]:
    return [str(p) for p in get_files(config.export_path)]


EXPECTED_DISCORD_STRUCTURE = ("messages/index.json", "account/user.json")

# reduces time by multiple minutes, after the cache is created
# HTML rendering can take quite a long time for the thousands of messages
@mcachew(depends_on=_cachew_depends_on, logger=logger)
def messages() -> Iterator[Message]:
    emitted: Set[int] = set()
    for exp in get_files(config.export_path):
        with match_structure(
            exp, expected=EXPECTED_DISCORD_STRUCTURE
        ) as discord_export:
            for message_dir in [d / "messages" for d in discord_export]:
                for msg in parse_messages(message_dir):
                    if msg.message_id in emitted:
                        continue
                    yield Message(
                        message_id=msg.message_id,
                        timestamp=msg.timestamp,
                        channel=msg.channel,
                        content=_remove_link_suppression(msg.content),
                        attachments=msg.attachments,
                    )
                    emitted.add(msg.message_id)


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def activity() -> Iterator[Activity]:
    emitted: Set[str] = set()
    for exp in get_files(config.export_path):
        with match_structure(
            exp, expected=EXPECTED_DISCORD_STRUCTURE
        ) as discord_export:
            for activity_dir in [d / "activity" for d in discord_export]:
                for act in parse_activity(activity_dir):
                    if act.event_id in emitted:
                        continue
                    yield act
                    emitted.add(act.event_id)


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(messages),
        **stat(activity),
    }

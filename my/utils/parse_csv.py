import csv
import logging

from pathlib import Path
from typing import Callable, Iterator, TypeVar, Optional

T = TypeVar("T")


def parse_csv_file(
    histfile: Path,
    parse_function: Callable[[str], Iterator[T]],
    logger: Optional[logging.Logger] = None,
) -> Iterator[T]:
    """
    Parses a CSV file using parse_function, yield results from that function.

    If the CSV file contains NUL bytes, replace those and try again.
    """
    with histfile.open("r", encoding="utf-8", newline="") as f:
        data = f.read()
        try:
            yield from parse_function(data)
        except (csv.Error, ValueError) as e:
            if "\0" not in data:
                raise RuntimeError(f"Could not parse {histfile}: {e}") from e
            else:
                if logger:
                    logger.warning("Found NUL byte in %s: %s", histfile, e)
                yield from parse_function(data.replace("\0", ""))

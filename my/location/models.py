from datetime import date, datetime
from typing import Union, Tuple

DateIsh = Union[datetime, date, str]

# todo hopefully reasonable? might be nice to add name or something too
LatLon = Tuple[float, float]

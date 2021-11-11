import datetime as dt
from typing import TypedDict


class ILatestRev(TypedDict):
    id: int
    revDt: dt.datetime
    latestGujRev: int
    latestRev: int

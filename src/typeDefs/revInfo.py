import datetime as dt
from typing import TypedDict


class IRevInfoRecord(TypedDict):
    id: int
    revDt: dt.datetime
    gujRev: int
    rev: int
    revTs: dt.datetime

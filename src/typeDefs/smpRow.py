import datetime as dt
from typing import TypedDict


class ISmpRow(TypedDict):
    dataTime: dt.datetime
    regTag: str
    smpVal: float
    rev: int

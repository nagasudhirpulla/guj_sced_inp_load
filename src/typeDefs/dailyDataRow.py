import datetime as dt
from typing import TypedDict


class IDailyDataRow(TypedDict):
    genId: int
    dataType: str
    targetDt: dt.datetime
    dataVal: float

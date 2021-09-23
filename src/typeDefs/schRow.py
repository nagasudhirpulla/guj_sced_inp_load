import datetime as dt
from typing import TypedDict


class ISchRow(TypedDict):
    schTime: dt.datetime
    genId: int
    schType: str
    schVal: float
    rev: int

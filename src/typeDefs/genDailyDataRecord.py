import datetime as dt
from typing import TypedDict


class IGenDailyDataRecord(TypedDict):
    genId: int
    name: str
    vc: float
    fuelType: str
    targetDt: dt.datetime
    avgPuCap: float
    tmPu: float
    rUpPu: float
    rDnPu: float

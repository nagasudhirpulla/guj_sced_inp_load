import datetime as dt
from typing import TypedDict


class IGenMasterRow(TypedDict):
    name: str
    vc: float
    fuelType: str
    targetDt: dt.datetime
    avgPuCap: float
    tmPu: float
    rUpPu: float
    rDnPu: float

import datetime as dt
from typing import TypedDict


class IGenObj(TypedDict):
    id: int
    name: str
    vcPu: float
    fuelType: str
    capPu: float
    tmPu: float
    rUpPu: float
    rDnPu: float

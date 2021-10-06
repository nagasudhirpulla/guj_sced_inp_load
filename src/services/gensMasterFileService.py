import datetime as dt
from typing import List

import pandas as pd
from src.typeDefs.genMasterRow import IGenMasterRow


def getGenMasterRowsFromFile(masterFilePath: str, masterFileSheetName: str, targetDt: dt.datetime) -> List[IGenMasterRow]:
    gensMasterDf = pd.read_excel(
        masterFilePath, sheet_name=masterFileSheetName)
    gensMasterDf = gensMasterDf[["Plant Name", "Variable Cost per unit",
                                 "Avg. Unit capacity", "Tech Min Per Unit", "Ramp Up per unit", "Ramp Dn per unit"]]
    gensMasterDf = gensMasterDf.dropna()
    gensMasterDf["fuelType"] = "coal"
    gensMasterDf["targetDt"] = targetDt
    gensMasterDf = gensMasterDf.rename(columns={"Plant Name": "name",
                                                "Variable Cost per unit": "vc",
                                                "Avg. Unit capacity": "avgPuCap",
                                                "Tech Min Per Unit": "tmPu",
                                                "Ramp Up per unit": "rUpPu",
                                                "Ramp Dn per unit": "rDnPu"})

    gensMasterRows: List[IGenMasterRow] = gensMasterDf.to_dict('records')
    return gensMasterRows

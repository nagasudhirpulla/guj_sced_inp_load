import datetime as dt
from typing import List, Dict

import pandas as pd
from src.typeDefs.genDailyDataRecord import IGenDailyDataRecord
from src.typeDefs.dailyDataRow import IDailyDataRow


def getGenMasterRowsFromFile(genIdsDict: Dict[str, int], masterFilePath: str, masterFileSheetName: str, targetDt: dt.datetime) -> List[IDailyDataRow]:
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

    gensMasterRows: List[IGenDailyDataRecord] = gensMasterDf.to_dict('records')

    # create daily data rows
    dailyDataRows = []
    for gItr in range(len(gensMasterRows)):
        genRow = gensMasterRows[gItr]
        genName = genRow["name"]
        if not genName in genIdsDict:
            print("{0} not found in the main generators list".format(genName))
            return []
        genId = genIdsDict[genName]
        genRow["genId"] = genId
        dailyDataRows.append({
            "genId": genId,
            "dataType": "vc",
            "targetDt": targetDt,
            "dataVal": genRow["vc"]
        })
        dailyDataRows.append({
            "genId": genId,
            "dataType": "avg_pu_cap",
            "targetDt": targetDt,
            "dataVal": genRow["avgPuCap"]
        })
        dailyDataRows.append({
            "genId": genId,
            "dataType": "tm_pu",
            "targetDt": targetDt,
            "dataVal": genRow["tmPu"]
        })
        dailyDataRows.append({
            "genId": genId,
            "dataType": "rup_pu",
            "targetDt": targetDt,
            "dataVal": genRow["rUpPu"]
        })
        dailyDataRows.append({
            "genId": genId,
            "dataType": "rdn_pu",
            "targetDt": targetDt,
            "dataVal": genRow["rDnPu"]
        })

    return dailyDataRows

import argparse
import datetime as dt
import os
from typing import List

import pandas as pd

from src.config.appConfig import loadAppConfig
from src.repos.gensMasterDataRepo import GensMasterRepo
from src.repos.schDataRepo import SchedulesRepo
from src.repos.dailyDataRepo import DailyDataRepo
from src.services.gensMasterFileService import getGenMasterRowsFromFile
from src.typeDefs.schRow import ISchRow
from src.typeDefs.dailyDataRow import IDailyDataRow

# read config file
appConf = loadAppConfig()
dbHost = appConf["dbHost"]
dbName = appConf["dbName"]
dbUname = appConf["dbUname"]
dbPass = appConf["dbPass"]
gamsExcelPath = appConf["gamsExcelPath"]

# make target date as tomorrow
targetDt = dt.datetime.now() + dt.timedelta(days=1)
targetDt = dt.datetime(targetDt.year, targetDt.month, targetDt.day)

# get target date from command line if present
parser = argparse.ArgumentParser()
parser.add_argument('--date', help='target Date')
args = parser.parse_args()
targetDtStr = args.date
if not targetDtStr == None:
    targetDt = dt.datetime.strptime(targetDtStr, "%Y-%m-%d")

# derive the filenames for the target date
inpFolderPath = appConf["folderPath"]
onbarFPath = os.path.join(inpFolderPath, "Declare Capacity_{0}.csv".format(
    dt.datetime.strftime(targetDt, '%d_%m_%Y')))
schFPath = os.path.join(inpFolderPath, "Injection Schedule_{0}.csv".format(
    dt.datetime.strftime(targetDt, '%d_%m_%Y')))

# check - check if relevant ON-BAR DC file is present
isOnbarFilePresent = os.path.isfile(onbarFPath)
if not isOnbarFilePresent:
    print("onbar file not present")

# check - check if relevant Schedule file is present
isSchFilePresent = os.path.isfile(schFPath)
if not isSchFilePresent:
    print("schedule file not present")

# exit if all files not present
if not all([isOnbarFilePresent, isSchFilePresent]):
    exit(0)

# get generators master data
gensRepo = GensMasterRepo(dbHost, dbName, dbUname, dbPass)
genIdsDict = gensRepo.getGenIds()

# get generator daywise data from excel file
gensDailyRows: IDailyDataRow = getGenMasterRowsFromFile(
    genIdsDict, gamsExcelPath, "Data", targetDt)

if len(gensDailyRows) == 0:
    print("No generators db rows derived in daily generators data excel")
    exit(0)

# push schedules data to db
dDataRepo = DailyDataRepo(dbHost, dbName, dbUname, dbPass)
isDailyRowsInsertSuccess = dDataRepo.insertRows(gensDailyRows)

if not isDailyRowsInsertSuccess:
    print("Unable to insert generators daily data rows into database")
    exit(0)

# get the list of required generators
reqGens = list(genIdsDict.keys())

# read data from onbar file
onbarDf = pd.read_csv(onbarFPath, nrows=96)
# check - check if all generators are present in onbar file
missingOnbarGens = [x for x in reqGens if x not in onbarDf.columns]
isAllDbGensInOnbarFile = len(missingOnbarGens) == 0
if not isAllDbGensInOnbarFile:
    print("all db gens are not present in onbar file")
    print(', '.join(missingOnbarGens))
    # make onbar DC = 0 for missing generators
    for mGen in missingOnbarGens:
        onbarDf[mGen] = 0

# read data from schedule file
schDf = pd.read_csv(schFPath, skiprows=None, nrows=96)
# check - check if all generators are present in onbar file
missingSchGens = [x for x in reqGens if x not in schDf.columns]
isAllDbGensInSchFile = len(missingSchGens) == 0
if not isAllDbGensInSchFile:
    print("all db gens are not present in schedule file")
    print(', '.join(missingSchGens))

if not all([isAllDbGensInSchFile]):
    exit(0)

# extract generators data from csv
onbarDf = onbarDf[reqGens]
schDf = schDf[reqGens]

# check - check if onbar data of input csv has 96 rows
isOnbarRows96 = onbarDf.shape[0] == 96
if not isOnbarRows96:
    print("onbar DC file does not have 96 rows")

# check - check if schedule data of input csv has 96 rows
isSchRows96 = schDf.shape[0] == 96
if not isSchRows96:
    print("Schedule file does not have 96 rows")


if not all([isAllDbGensInOnbarFile, isAllDbGensInSchFile]):
    exit(0)

# create rows for db insertion
dbRows: List[ISchRow] = []
for rIter in range(onbarDf.shape[0]):
    for g in reqGens:
        onbarRow: ISchRow = {
            "schTime": targetDt+dt.timedelta(minutes=rIter*15),
            "genId": genIdsDict[g],
            "schType": "onbar",
            "schVal": float(onbarDf[g].iloc[rIter]),
            "rev": 0
        }
        dbRows.append(onbarRow)
        schRow: ISchRow = {
            "schTime": targetDt+dt.timedelta(minutes=rIter*15),
            "genId": genIdsDict[g],
            "schType": "sch",
            "schVal": float(schDf[g].iloc[rIter]),
            "rev": 0
        }
        dbRows.append(schRow)

# push schedules data to db
schRepo = SchedulesRepo(dbHost, dbName, dbUname, dbPass)
isSchInsertSuccess = schRepo.insertSchedules(dbRows)

print("Insertion status = {0}".format(isSchInsertSuccess))
print("SCED input files data loading program complete...")

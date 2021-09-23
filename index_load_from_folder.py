import argparse
import datetime as dt
import os
from typing import List

import pandas as pd

from src.config.appConfig import loadAppConfig
from src.repos.gensMasterDataRepo import GensMasterRepo
from src.repos.schDataRepo import SchedulesRepo
from src.typeDefs.schRow import ISchRow

# read config file
appConf = loadAppConfig()
dbHost = appConf["dbHost"]
dbName = appConf["dbName"]
dbUname = appConf["dbUname"]
dbPass = appConf["dbPass"]

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

# check if relevant ON-BAR DC file is present
isOnbarFilePresent = os.path.isfile(onbarFPath)
if not isOnbarFilePresent:
    print("onbar file not present")

# check if relevant Schedule file is present
isSchFilePresent = os.path.isfile(schFPath)
if not isSchFilePresent:
    print("schedule file not present")

# exit if all files not present
if not all([isOnbarFilePresent, isSchFilePresent]):
    exit(0)


# get generators master data
gensRepo = GensMasterRepo(
    appConf["dbHost"], appConf["dbName"], appConf["dbUname"], appConf["dbPass"])
genIdsDict = gensRepo.getGenIds()

# get the list of required generators
reqGens = list(genIdsDict.keys())

# read data from onbar file
onbarDf = pd.read_csv(onbarFPath, nrows=96)

# check if all generators are present in onbar file
onbarGens = [x for x in onbarDf.columns if x in reqGens]

# extract generators data from csv
onbarDf = onbarDf[onbarGens]

# read data from schedule file
schDf = pd.read_csv(schFPath, skiprows=1, nrows=96)
schDf = onbarDf[reqGens]


# check if onbar data has 96 rows
isOnbarRows96 = onbarDf.shape[0] == 96
if not isOnbarRows96:
    print("onbar DC file does not have 96 rows")

# check if schedule data has 96 rows
isSchRows96 = schDf.shape[0] == 96
if not isSchRows96:
    print("Schedule file does not have 96 rows")

# check if all on bar gens are present in sch df
isOnbarGensInSchGens = len(
    [x for x in schDf.columns if not (x in onbarGens)]) == 0
if not isOnbarGensInSchGens:
    print("All onbar dc generators are not present in schedule generators")

if not all([isOnbarRows96, isSchRows96, isOnbarGensInSchGens]):
    exit(0)


# create rows for db insertion
dbRows: List[ISchRow] = []
for rIter in range(onbarDf.shape[0]):
    for g in onbarGens:
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

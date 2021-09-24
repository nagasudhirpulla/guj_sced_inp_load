import argparse
import datetime as dt
import os

import openpyxl
import pandas as pd

from src.config.appConfig import loadAppConfig
from src.repos.gensMasterDataRepo import GensMasterRepo
from src.repos.schDataRepo import SchedulesRepo
from src.services.gamsService import runGams
from src.typeDefs.schRow import ISchRow

# read config file
appConf = loadAppConfig()
dbHost = appConf["dbHost"]
dbName = appConf["dbName"]
dbUname = appConf["dbUname"]
dbPass = appConf["dbPass"]
gamsExePath = appConf["gamsExePath"]
gamsCodePath = appConf["gamsCodePath"]
gamsLstPath = appConf["gamsLstPath"]

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
gamsExcelPath = appConf["gamsExcelPath"]
# check if gams excel file exists
isGamsExcelPresent = os.path.isfile(gamsExcelPath)

if not isGamsExcelPresent:
    print("GAMS input excel not present...")
    exit(0)

# get the generators info from db
gensRepo = GensMasterRepo(
    appConf["dbHost"], appConf["dbName"], appConf["dbUname"], appConf["dbPass"])
gens = gensRepo.getGens()

gamsExcel = openpyxl.load_workbook(gamsExcelPath)

# write data to generators data sheet
# Data sheet column numbers
gensSheetName = "Data"
stationColNum = 3
vcColNum = 8
unitCapColNum = 11
tmColNum = 12
rUpColNum = 13
rDnColNum = 14
if not gensSheetName in gamsExcel.sheetnames:
    print('Generators data sheet does not exist in gams input excel file')
    exit(0)
gensSheet = gamsExcel[gensSheetName]
for gItr, g in enumerate(gens):
    gensSheet.cell(row=gItr+2, column=stationColNum).value = g["name"]
    gensSheet.cell(row=gItr+2, column=vcColNum).value = g["vcPu"]
    gensSheet.cell(row=gItr+2, column=unitCapColNum).value = g["capPu"]
    gensSheet.cell(row=gItr+2, column=tmColNum).value = g["tmPu"]
    gensSheet.cell(row=gItr+2, column=rUpColNum).value = g["rUpPu"]
    gensSheet.cell(row=gItr+2, column=rDnColNum).value = g["rDnPu"]

# write data to generators onbar sheet
onbarSheetName = "DCOnbar"
if not onbarSheetName in gamsExcel.sheetnames:
    print('Onbar data sheet does not exist in gams input excel file')
    exit(0)
onbarSheet = gamsExcel[onbarSheetName]

# fetch onbar data
schRepo = SchedulesRepo(dbHost, dbName, dbUname, dbPass)

# populate data to onbar sheet
for gItr, g in enumerate(gens):
    onbarSheet.cell(row=gItr+2, column=1).value = g["name"]
    onbarSheet.cell(row=gItr+2, column=2).value = 1

    genOnbarRows = schRepo.getGenSchedules(
        "onbar", g["id"], 0, targetDt, targetDt+dt.timedelta(hours=23, minutes=59))
    # check if we got 96 rows
    if not len(genOnbarRows) == 96:
        print("96 rows not present in onabar data of {0} for the date {1}".format(
            g["name"], targetDt))
        exit(0)

    for blkItr in range(len(genOnbarRows)):
        onbarSheet.cell(row=gItr+2, column=blkItr +
                        3).value = genOnbarRows[blkItr]["schVal"]

# write data to generators onbar sheet
schSheetName = "Schedule"
if not schSheetName in gamsExcel.sheetnames:
    print('Onbar data sheet does not exist in gams input excel file')
    exit(0)
schSheet = gamsExcel[schSheetName]

# populate data to onbar sheet
for gItr, g in enumerate(gens):
    schSheet.cell(row=gItr+2, column=1).value = g["name"]
    schSheet.cell(row=gItr+2, column=2).value = 1

    genSchRows = schRepo.getGenSchedules(
        "sch", g["id"], 0, targetDt, targetDt+dt.timedelta(hours=23, minutes=59))
    # check if we got 96 rows
    if not len(genSchRows) == 96:
        print("96 rows not present in schedule data of {0} for the date {1}".format(
            g["name"], targetDt))
        exit(0)

    for blkItr in range(len(genSchRows)):
        schSheet.cell(row=gItr+2, column=blkItr +
                      3).value = genSchRows[blkItr]["schVal"]

gamsExcel.save(gamsExcelPath)
gamsExcel.close()

# run GAMS on excel data
isGamsExecSuccess = runGams(gamsExePath, gamsCodePath, gamsLstPath)
if not isGamsExecSuccess:
    print("GAMS execution was not successful...")
    exit(0)

# push output data from GAMS excel to db
resultsSheetName = "Result Report"
if not (resultsSheetName in gamsExcel.sheetnames):
    print('GAMS results data sheet does not exist in gams excel file...')
    exit(0)

# read dataframe from output sheet
gamsResDf = pd.read_excel(gamsExcelPath, sheet_name=resultsSheetName)
gamsResCols = gamsResDf.columns.tolist()
if len(gamsResCols) < 98:
    print("result sheet does not have at least 98 columns...")
    exit()

gamsResCols = gamsResCols[0:98]

# check if all the blocks columns are present in the result sheet
isAllBlksInResPresent = all([(x in gamsResCols) for x in range(1, 97)])
if not isAllBlksInResPresent:
    print("result sheet does not have columns named 1 to 96")
    exit(0)

# check if all generators are present in database
resGens = gamsResDf.iloc[:, 0].tolist()
dbGenNames = [g["name"] for g in gens]
isAllDbGensInRes = all([(x in resGens) for x in dbGenNames])
if not isAllDbGensInRes:
    print("All DB generators are not in GAMS result sheet")
    exit(0)

# get generator names dictionary
genIdsDict = {}
for g in gens:
    genIdsDict[g["name"]] = g["id"]

optSchRows = []
for genItr in range(gamsResDf.shape[0]):
    genName = gamsResDf.iloc[genItr, 0]
    if not genName in genIdsDict:
        continue
    genId = genIdsDict[genName]
    for blk in range(1, 97):
        schVal = gamsResDf[blk].iloc[genItr]
        schRow: ISchRow = {
            "schTime": targetDt+dt.timedelta(minutes=15*(blk-1)),
            "genId": genId,
            "schType": "opt",
            "schVal": schVal,
            "rev": 0
        }
        optSchRows.append(schRow)

# push schedules data to db
isSchInsertSuccess = schRepo.insertSchedules(optSchRows)
print("Optimal Schedule Insertion status = {0}".format(isSchInsertSuccess))

print("execution complete...")

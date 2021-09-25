import argparse
import datetime as dt
import os

import pandas as pd
from openpyxl import Workbook

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
gamsExePath = appConf["gamsExePath"]
gamsCodePath = appConf["gamsCodePath"]
gamsLstPath = appConf["gamsLstPath"]
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

resDumpFolder = appConf["resultsDumpFolder"]
# check - check if results dumping folder exists
if not os.path.isdir(resDumpFolder):
    print("results dumping folder doesnot exist...")
    exit(0)

# create workbook object to dump excel data
wb = Workbook()

# get the generators info from db
gensRepo = GensMasterRepo(
    dbHost, dbName, dbUname, dbPass)
gens = gensRepo.getGens()

# write generators master data
gensSheet = wb.active
gensSheet.title = "Data"
stationColNum = 3
vcColNum = 8
unitCapColNum = 11
tmColNum = 12
rUpColNum = 13
rDnColNum = 14
# populate header for 1st row
gensSheet.cell(row=1, column=stationColNum).value = "Plant Name"
gensSheet.cell(row=1, column=vcColNum).value = "Variable Cost per unit"
gensSheet.cell(
    row=1, column=unitCapColNum).value = "Avg. Unit capacity"
gensSheet.cell(row=1, column=tmColNum).value = "Tech Min Per Unit"
gensSheet.cell(row=1, column=rUpColNum).value = "Ramp Up per unit"
gensSheet.cell(row=1, column=rDnColNum).value = "Ramp Dn per unit"
for gItr, g in enumerate(gens):
    # populate generator data
    gensSheet.cell(row=gItr+2, column=stationColNum).value = g["name"]
    gensSheet.cell(row=gItr+2, column=vcColNum).value = g["vcPu"]
    gensSheet.cell(row=gItr+2, column=unitCapColNum).value = g["capPu"]
    gensSheet.cell(row=gItr+2, column=tmColNum).value = g["tmPu"]
    gensSheet.cell(row=gItr+2, column=rUpColNum).value = g["rUpPu"]
    gensSheet.cell(row=gItr+2, column=rDnColNum).value = g["rDnPu"]

# fetch onbar data
schRepo = SchedulesRepo(dbHost, dbName, dbUname, dbPass)

# create onbar sheet
onbarSheet = wb.create_sheet("DCOnbar")
# populate onbar header to onbar sheet
onbarSheet.cell(row=1, column=1).value = "Plant Name"
onbarSheet.cell(row=1, column=2).value = "Region"
for blk in range(1, 97):
    onbarSheet.cell(row=1, column=blk+2).value = blk

# populate onbar data to onbar sheet
for gItr, g in enumerate(gens):
    onbarSheet.cell(row=gItr+2, column=1).value = g["name"]
    onbarSheet.cell(row=gItr+2, column=2).value = 1

    genOnbarRows = schRepo.getGenSchedules(
        "onbar", g["id"], 0, targetDt, targetDt+dt.timedelta(hours=23, minutes=59))
    # check - check if we got 96 rows for loading onbar data for a generator for the desired date
    if not len(genOnbarRows) == 96:
        print("96 rows not present in onbar data of {0} for the date {1}".format(
            g["name"], targetDt))
        exit(0)

    for blkItr in range(len(genOnbarRows)):
        onbarSheet.cell(row=gItr+2, column=blkItr +
                        3).value = genOnbarRows[blkItr]["schVal"]

# create schedule sheet
schSheet = wb.create_sheet("Schedule")
# populate schedules header to schedules sheet
schSheet.cell(row=1, column=1).value = "Plant Name"
schSheet.cell(row=1, column=2).value = "Region"
for blk in range(1, 97):
    schSheet.cell(row=1, column=blk+2).value = blk

# populate schedule data to Schedule sheet
for gItr, g in enumerate(gens):
    schSheet.cell(row=gItr+2, column=1).value = g["name"]
    schSheet.cell(row=gItr+2, column=2).value = 1

    genSchRows = schRepo.getGenSchedules(
        "sch", g["id"], 0, targetDt, targetDt+dt.timedelta(hours=23, minutes=59))
    # check - check if we got 96 rows for loading onbar data for a generator for the desired date
    if not len(genSchRows) == 96:
        print("96 rows not present in schedule data of {0} for the date {1}".format(
            g["name"], targetDt))
        exit(0)

    for blkItr in range(len(genSchRows)):
        schSheet.cell(row=gItr+2, column=blkItr +
                      3).value = genSchRows[blkItr]["schVal"]

# create Optimal Schedule sheet
optSheet = wb.create_sheet("Optimal Schedule")
# populate schedules header to schedules sheet
optSheet.cell(row=1, column=1).value = "Plant Name"
optSheet.cell(row=1, column=2).value = "Region"
for blk in range(1, 97):
    optSheet.cell(row=1, column=blk+2).value = blk

# populate optimal schedule data to optimal schedule sheet
for gItr, g in enumerate(gens):
    optSheet.cell(row=gItr+2, column=1).value = g["name"]
    optSheet.cell(row=gItr+2, column=2).value = 1

    genOptRows = schRepo.getGenSchedules(
        "opt", g["id"], 0, targetDt, targetDt+dt.timedelta(hours=23, minutes=59))
    # check - check if we got 96 rows for loading onbar data for a generator for the desired date
    if not len(genOptRows) == 96:
        print("96 rows not present in optimal schedule data of {0} for the date {1}".format(
            g["name"], targetDt))
        exit(0)

    for blkItr in range(len(genOptRows)):
        optSheet.cell(row=gItr+2, column=blkItr +
                      3).value = genOptRows[blkItr]["schVal"]

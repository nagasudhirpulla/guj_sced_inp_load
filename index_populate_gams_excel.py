import argparse
import datetime as dt
import os
from typing import List

import pandas as pd

from src.config.appConfig import loadAppConfig
from src.repos.gensMasterDataRepo import GensMasterRepo
from src.repos.schDataRepo import SchedulesRepo
from src.typeDefs.schRow import ISchRow

import openpyxl

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
gamsExcelPath = appConf["gamsExcelPath"]
# check if gams excel file exists
isGamsExcelPresent = os.path.isfile(gamsExcelPath)

if not isGamsExcelPresent:
    print("GAMS input excel not present...")
    exit(0)

# Data sheet column numbers
gensSheetName = "Data"
stationColNum = 3
vcColNum = 8
unitCapColNum = 11
tmColNum = 12
rUpColNum = 13
rDnColNum = 14

# get the generators info from db
gensRepo = GensMasterRepo(
    appConf["dbHost"], appConf["dbName"], appConf["dbUname"], appConf["dbPass"])
gens = gensRepo.getGens()

gamsExcel = openpyxl.load_workbook(gamsExcelPath)

# write data to generators data sheet
if gensSheetName in gamsExcel.sheetnames:
    print('Generators data sheet does not exist in gams input excel file')
gensSheet = gamsExcel[gensSheetName]
for gItr, g in enumerate(gens):
    gensSheet.cell(row=gItr+2, column=stationColNum).value = g["name"]
    gensSheet.cell(row=gItr+2, column=vcColNum).value = g["vcPu"]
    gensSheet.cell(row=gItr+2, column=unitCapColNum).value = g["capPu"]
    gensSheet.cell(row=gItr+2, column=tmColNum).value = g["tmPu"]
    gensSheet.cell(row=gItr+2, column=rUpColNum).value = g["rUpPu"]
    gensSheet.cell(row=gItr+2, column=rDnColNum).value = g["rDnPu"]

print("execution complete...")

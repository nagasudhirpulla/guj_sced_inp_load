import argparse
import datetime as dt
import os
from typing import List

import pandas as pd

from src.config.appConfig import loadAppConfig
from src.repos.gensMasterDataRepo import GensMasterRepo
from src.repos.schDataRepo import SchedulesRepo
from src.typeDefs.schRow import ISchRow

from openpyxl import load_workbook

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


import argparse
import datetime as dt
import os
import pandas as pd

from src.config.appConfig import loadAppConfig

# read config file
appConf = loadAppConfig()

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
onbarFPath = os.path.join(inpFolderPath, "NEXTDAY_DC_ON_BAR_SCED_{0}.csv".format(
    dt.datetime.strftime(targetDt, '%d-%b-%Y')))
schFPath = os.path.join(inpFolderPath, "NEXTDAY_SCHEDULE_SCED_{0}.csv".format(
    dt.datetime.strftime(targetDt, '%d-%b-%Y')))

# check if relevant ON-BAR DC file is present
isOnbarFilePresent = os.path.isfile(onbarFPath)
if not isOnbarFilePresent:
    print("onbar file not present")

# check if relevant Schedule file is present
isSchFilePresent = os.path.isfile(schFPath)
if not isSchFilePresent:
    print("schedule file not present")

# exit if all files not present
if (not isOnbarFilePresent) or (not isSchFilePresent):
    exit(0)

# get the list of required generators
reqGens = appConf["gens"]

# read data from onbar file
onbarDf = pd.read_csv(onbarFPath, skiprows=1)

# check if all generators are present in onbar file
onbarGens = [x for x in onbarDf.columns if x in reqGens]

# extract generators data from csv
onbarDf = onbarDf[onbarGens]

# read data from schedule file
schDf = pd.read_csv(schFPath, skiprows=1)
schDf = onbarDf[reqGens]


# check if onbar data has 96 rows
isOnbarRows96 = onbarDf.shape[0] == 96

# check if schedule data has 96 rows
isSchRows96 = schDf.shape[0] == 96

# check if all on bar gens are present in sch df
isOnbarGensInSchGens = len(
    [x for x in schDf.columns if not (x in onbarGens)]) == 0

if not isOnbarGensInSchGens:
    print("All onbar dc generators are not present in schedule generators")
    exit(0)

# create rows for db insertion
for rIter in onbarDf.shape[0]:
    1 == 1
# read the data and push to db

import argparse
import datetime as dt
import glob
import os
from typing import Dict, List, Optional, TypedDict

import pandas as pd

from src.app.filenames.extractTargetDtFnames import extractTargetDtFnames
from src.app.filenames.extractTsFromRevInfoStr import extractTsFromRevInfoStr
from src.app.filenames.fileTypes import ONBAR_FILE_TYPE, SCH_FILE_TYPE
from src.config.appConfig import loadAppConfig
from src.repos.dailyDataRepo import DailyDataRepo
from src.repos.gensMasterDataRepo import GensMasterRepo
from src.repos.latestRevData import LatestRevsRepo
from src.repos.revsInfo import RevsInfoRepo
from src.repos.schDataRepo import SchedulesRepo
from src.services.gensMasterFileService import getGenMasterRowsFromFile
from src.typeDefs.dailyDataRow import IDailyDataRow
from src.typeDefs.schRow import ISchRow
from src.typeDefs.revInfo import IRevInfoRecord

print("SCED input files data loading program start...")
# read config file
appConf = loadAppConfig()
remoteFilesDirectory = appConf["ftpFolderPath"]
inpFolderPath: str = appConf["folderPath"]
ftpHost = appConf["ftpHost"]
ftpUname = appConf["ftpUname"]
ftpPass = appConf["ftpPass"]
dbHost = appConf["dbHost"]
dbName = appConf["dbName"]
dbUname = appConf["dbUname"]
dbPass = appConf["dbPass"]
gamsExcelPath = appConf["gamsExcelPath"]

# make target date as today
targetDt = dt.datetime.now()
targetDt = dt.datetime(targetDt.year, targetDt.month, targetDt.day)

# get target date from command line if present
parser = argparse.ArgumentParser()
parser.add_argument('--date', help='target Date')
parser.add_argument('--doff', help='Date offset')
parser.add_argument('--rev', help='revision number')
parser.add_argument('--single', action="store_true")
args = parser.parse_args()
targetDtStr = args.date
if not targetDtStr == None:
    targetDt = dt.datetime.strptime(targetDtStr, "%Y-%m-%d")
targetDtOffsetStr = args.doff
targetDtOffset = 0
if not targetDtOffsetStr == None:
    targetDtOffset = int(targetDtOffsetStr)
# add offset days to target date
targetDt = targetDt + dt.timedelta(days=targetDtOffset)

# flag that specifies to process only target revision and avoid processing revisions beyond this revision
isProcessOnlyOneRev = args.single

targetGujRevStr = args.rev
targetGujRev = None
if not targetGujRevStr == None:
    targetGujRev = int(targetGujRevStr)


latRevRepo = LatestRevsRepo(dbHost, dbName, dbUname, dbPass)
# if revision number is not specified from cli, then latest revision number for the date is to be determined from db
# if no latest revision number is found for the date, then the latest revision number for the date is 0
if targetGujRev == None:
    latestRevInfo = latRevRepo.getLatestRevForDate(targetDt)
    if latestRevInfo == None:
        targetGujRev = 0
    else:
        targetGujRev = latestRevInfo["latestGujRev"]+1

# get all filename from input folder
folderFileNames = glob.glob(r'{0}\*.csv'.format(inpFolderPath))
folderFileNames = [os.path.split(x)[1] for x in folderFileNames]
# check for required filenames to be downloaded from ftp location
targetDtFtpFiles = extractTargetDtFnames(folderFileNames, targetDt)


class RevFileDataObj(TypedDict):
    schFile: Optional[str]
    onbarFile: Optional[str]
    revTime: Optional[dt.datetime]
    localRevNum: Optional[int]


# retain files info as per desired revision numbers
revFilesInfo: Dict[int, RevFileDataObj] = {}

# get all target revision data files info from input folder
for fInfo in targetDtFtpFiles:
    fRev = fInfo["revNum"]
    if fRev < targetGujRev:
        continue
    # Whether all revisions above target revision to be processed is determined by isProcessOnlyOneRev flag
    if not(fRev == targetGujRev) and isProcessOnlyOneRev:
        continue
    # create key in dict if not present
    if not (fRev in revFilesInfo):
        revFilesInfo[fRev] = {"schFile": None,
                              "onbarFile": None, "revTime": None, "localRevNum": None}
    # create entry in revision files info dictionary
    if fInfo["fileType"] == ONBAR_FILE_TYPE:
        revFilesInfo[fRev]["onbarFile"] = fInfo["name"]
    elif fInfo["fileType"] == SCH_FILE_TYPE:
        schFname = fInfo["name"]
        revFilesInfo[fRev]["schFile"] = schFname
        # get revision time from schedule file
        try:
            with open(os.path.join(inpFolderPath, schFname), 'r') as schCsvReader:
                revInfoStr: str = schCsvReader.readlines()[0].split(",")[
                    0].strip()
                revTs = extractTsFromRevInfoStr(revInfoStr)
                revFilesInfo[fRev]["revTime"] = revTs
        except:
            revFilesInfo[fRev]["revTime"] = None

# discard files with incomplete data
targetGujRevNums = list(revFilesInfo.keys())
for fRev in targetGujRevNums:
    isDiscardReq = False
    # derive minimum timestamp for discarding very early revisions <= 19:00 of target day-1
    minRevTs = targetDt-dt.timedelta(days=1)
    minRevTs = dt.datetime(minRevTs.year, minRevTs.month,
                           minRevTs.day, 19, 0, 0)
    revTs = revFilesInfo[fRev]["revTime"]

    # discard based on revision timestamp
    if not isinstance(revTs, dt.datetime):
        isDiscardReq = True
    elif revTs <= minRevTs:
        isDiscardReq = True

    if (revFilesInfo[fRev]["schFile"] == None) or (revFilesInfo[fRev]["onbarFile"] == None):
        # discard the revisions where we do not have both schedule and onbar files
        isDiscardReq = True

    if isDiscardReq:
        # remove file info of undesired file
        _ = revFilesInfo.pop(fRev)

targetGujRevNums: List[int] = list(revFilesInfo.keys())
targetGujRevNums.sort()

revsInfoRepo = RevsInfoRepo(dbHost, dbName, dbUname, dbPass)

# determine the local revision for each gujarat revision to be processed
for gujRev in targetGujRevNums:
    localRev = None
    # get rev info from db for this guj revision
    revInfo: Optional[IRevInfoRecord] = revsInfoRepo.getGujRevInfo(
        targetDt, gujRev)
    if revInfo == None:
        # if this gujarat revision was not used in db, create a new revision in db
        # get max revision entry from db for the target date
        maxRevInfo = revsInfoRepo.getMaxLocalRevObjForDate(targetDt)
        if maxRevInfo == None:
            # since no revision was registered for this date, take required revision as 0
            localRev = 0
        else:
            # make required revision as 1 + max_local_revision for the target date
            localRev = maxRevInfo["rev"]+1
        isRevInfoInsertSuccess = revsInfoRepo.insertRevInfo(
            targetDt, gujRev, localRev, revFilesInfo[gujRev]["revTime"])
        if not isRevInfoInsertSuccess:
            localRev = None
    else:
        localRev = revInfo["rev"]
    revFilesInfo[gujRev]["localRevNum"] = localRev

# get generators master data
gensRepo = GensMasterRepo(dbHost, dbName, dbUname, dbPass)
genIdsDict = gensRepo.getGenIds()

# push the csv files data to db
numRevsPushed = 0
for gujRev in targetGujRevNums:
    print("processing csv files for date = {0}, guj rev = {1}".format(
        targetDt, gujRev))
    localRev = revFilesInfo[gujRev]["localRevNum"]
    if localRev == None:
        print("unable to create local revision for guj rev = {0} for date = {1}".format(
            gujRev, targetDt))
        continue
    onbarFPath = os.path.join(inpFolderPath, revFilesInfo[gujRev]["onbarFile"])
    schFPath = os.path.join(inpFolderPath, revFilesInfo[gujRev]["schFile"])

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
    # check - check if all generators are present in sch file
    missingSchGens = [x for x in reqGens if x not in schDf.columns]
    isAllDbGensInSchFile = len(missingSchGens) == 0
    if not isAllDbGensInSchFile:
        print("all db gens are not present in schedule file")
        print(', '.join(missingSchGens))

    if not all([isAllDbGensInSchFile]):
        # skip insertion since we all required gens are not present in sch file
        continue

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

    if not all([isOnbarRows96, isSchRows96]):
        # skip insertion since 96 rows are present in the csv files
        continue

    # create rows for db insertion
    dbRows: List[ISchRow] = []
    for rIter in range(onbarDf.shape[0]):
        for g in reqGens:
            onbarRow: ISchRow = {
                "schTime": targetDt+dt.timedelta(minutes=rIter*15),
                "genId": genIdsDict[g],
                "schType": "onbar",
                "schVal": float(onbarDf[g].iloc[rIter]),
                "rev": localRev
            }
            dbRows.append(onbarRow)
            schRow: ISchRow = {
                "schTime": targetDt+dt.timedelta(minutes=rIter*15),
                "genId": genIdsDict[g],
                "schType": "sch",
                "schVal": float(schDf[g].iloc[rIter]),
                "rev": localRev
            }
            dbRows.append(schRow)

    # push schedules data to db
    schRepo = SchedulesRepo(dbHost, dbName, dbUname, dbPass)
    isSchInsertSuccess = schRepo.insertSchedules(dbRows)
    print("Insertion status = {0} for gujRev = {1}, localRev = {2}".format(
        isSchInsertSuccess, gujRev, localRev))
    if isSchInsertSuccess:
        numRevsPushed += 1

print("number of revisions loaded into db = {0}".format(numRevsPushed))

# if at-least one file is processed, then push daywise master data files also into db from gams excel
if not numRevsPushed == 0:
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

print("SCED input files data loading program complete...")

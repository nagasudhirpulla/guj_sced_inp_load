import argparse
import datetime as dt
import os
from typing import Dict

from src.app.filenames.extractTargetDtFnames import extractTargetDtFnames
from src.config.appConfig import loadAppConfig
from src.repos.latestRevData import LatestRevsRepo
from src.services.ftpService import downloadFilesFromFtp, getFtpFilenames

print("SCED FTP files downloading program start...")

# read config file
appConf = loadAppConfig()
remoteFilesDirectory = appConf["ftpFolderPath"]
inpFolderPath = appConf["folderPath"]
ftpHost = appConf["ftpHost"]
ftpUname = appConf["ftpUname"]
ftpPass = appConf["ftpPass"]
dbHost = appConf["dbHost"]
dbName = appConf["dbName"]
dbUname = appConf["dbUname"]
dbPass = appConf["dbPass"]

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


# get all ftp filenames
ftpFnames = getFtpFilenames(ftpHost, ftpUname, ftpPass, remoteFilesDirectory)
# check for required filenames to be downloaded from ftp location
targetFtpFiles = extractTargetDtFnames(ftpFnames, targetDt)

# based on latest processed revision download only rest of the files
if isProcessOnlyOneRev:
    targetFtpFiles = [x for x in targetFtpFiles if (
        x["revNum"] == targetGujRev)]
else:
    targetFtpFiles = [x for x in targetFtpFiles if (
        x["revNum"] >= targetGujRev)]

if len(targetFtpFiles) == 0:
    print("No new unprocessed files found in ftp location, hence exiting without download...")
    exit(0)

print("started downloading ftp files ...")

isFtpDownloadSuccess = downloadFilesFromFtp(
    [os.path.join(inpFolderPath, x["name"]) for x in targetFtpFiles], [x["name"] for x in targetFtpFiles], ftpHost, ftpUname, ftpPass, remoteFilesDirectory)
print("file download status = {0}".format(isFtpDownloadSuccess))

print("SCED FTP files downloading program complete...")

import argparse
import datetime as dt
import os
from typing import Dict
from src.app.filenames.extractTargetDtFnames import extractTargetDtFnames

from src.config.appConfig import loadAppConfig
from src.services.ftpService import downloadFilesFromFtp, getFtpFilenames

# read config file
appConf = loadAppConfig()
remoteFilesDirectory = appConf["ftpFolderPath"]
inpFolderPath = appConf["folderPath"]
ftpHost = appConf["ftpHost"]
ftpUname = appConf["ftpUname"]
ftpPass = appConf["ftpPass"]

# make target date as today
targetDt = dt.datetime.now()
targetDt = dt.datetime(targetDt.year, targetDt.month, targetDt.day)

# get target date from command line if present
parser = argparse.ArgumentParser()
parser.add_argument('--date', help='target Date')
parser.add_argument('--doff', help='Date offset')
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


# get all ftp filenames
ftpFnames = getFtpFilenames(ftpHost, ftpUname, ftpPass, remoteFilesDirectory)
# check for required filenames to be downloaded from ftp location
targetFtpFiles = extractTargetDtFnames(ftpFnames, targetDt)


print("started downloading ftp files ...")

isFtpDownloadSuccess = downloadFilesFromFtp(
    [os.path.join(inpFolderPath, x["name"]) for x in targetFtpFiles], [x["name"] for x in targetFtpFiles], ftpHost, ftpUname, ftpPass, remoteFilesDirectory)
print("file download status = {0}".format(isFtpDownloadSuccess))

print("SCED FTP files downloading program complete...")

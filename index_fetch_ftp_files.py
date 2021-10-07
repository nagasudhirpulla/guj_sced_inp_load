import argparse
import datetime as dt
import os

from src.config.appConfig import loadAppConfig
from src.services.ftpService import downloadFileFromFtp

# read config file
appConf = loadAppConfig()
remoteFilesDirectory = appConf["ftpFolderPath"]
inpFolderPath = appConf["folderPath"]
ftpHost = appConf["ftpHost"]
ftpUname = appConf["ftpUname"]
ftpPass = appConf["ftpPass"]

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

targetDtNameStr = dt.datetime.strftime(targetDt, '%d_%m_%Y')
# derive the filenames for the target date
onbarTargetFName = "Declared Capacity_{0}.csv".format(targetDtNameStr)
onbarFPath = os.path.join(
    inpFolderPath, "Declare Capacity_{0}.csv".format(targetDtNameStr))

schTargetFName = "Injection Schedule_{0}.csv".format(targetDtNameStr)
schFPath = os.path.join(
    inpFolderPath, "Injection Schedule_{0}.csv".format(targetDtNameStr))

isOnbarFileFtpDownloadSuccess = downloadFileFromFtp(
    onbarFPath, onbarTargetFName, ftpHost, ftpUname, ftpPass, remoteFilesDirectory)
print("Onbar data file download = {0}".format(isOnbarFileFtpDownloadSuccess))

isSchFileFtpDownloadSuccess = downloadFileFromFtp(
    schFPath, schTargetFName, ftpHost, ftpUname, ftpPass, remoteFilesDirectory)
print("Schedule data file download = {0}".format(isSchFileFtpDownloadSuccess))

print("SCED FTP files downloading program complete...")

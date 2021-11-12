import ftplib
import os
import time
from typing import List


def uploadFileToFtp(localFilePath: str, ftpHost: str, ftpUname: str, ftpPass: str, remoteWorkingDirectory: str) -> bool:
    isUploadSuccess: bool = False
    _, targetFilename = os.path.split(localFilePath)
    # connect to the FTP server
    ftp = ftplib.FTP(timeout=30)
    ftp.connect(ftpHost, 21)
    time.sleep(2)
    ftp.login(ftpUname, ftpPass)
    time.sleep(2)
    if not (remoteWorkingDirectory == None or remoteWorkingDirectory.strip() == ""):
        _ = ftp.cwd(remoteWorkingDirectory)
        time.sleep(3)

    # Read file in binary mode
    with open(localFilePath, "rb") as file:
        retCode = ftp.storbinary(
            f"STOR {targetFilename}", file, blocksize=1024*1024)
        time.sleep(2)

    # quit and close the connection
    ftp.quit()

    if retCode.startswith('226'):
        isUploadSuccess = True
    return isUploadSuccess


def downloadFilesFromFtp(localFilePaths: List[str], targetFilenames: List[str], ftpHost: str, ftpUname: str, ftpPass: str, remoteWorkingDirectory: str) -> bool:
    isDownloadSuccess: bool = False
    if not len(localFilePaths) == len(targetFilenames):
        return isDownloadSuccess
    # connect to the FTP server
    ftp = ftplib.FTP(timeout=30)
    ftp.connect(ftpHost, 21)
    time.sleep(2)
    ftp.login(ftpUname, ftpPass)
    time.sleep(2)
    if not (remoteWorkingDirectory == None or remoteWorkingDirectory.strip() == ""):
        _ = ftp.cwd(remoteWorkingDirectory)
        time.sleep(3)

    # Read file in binary mode
    for fItr in range(len(localFilePaths)):
        localFilePath = localFilePaths[fItr]
        targetFilename = targetFilenames[fItr]
        print("downloading file from ftp = {0}".format(targetFilename))
        with open(localFilePath, "wb") as file:
            retCode = ftp.retrbinary("RETR " + targetFilename, file.write)
            time.sleep(2)

    # quit and close the connection
    ftp.quit()

    if retCode.startswith('226'):
        isDownloadSuccess = True
    return isDownloadSuccess


def getFtpFilenames(ftpHost: str, ftpUname: str, ftpPass: str, remoteWorkingDirectory: str) -> List[str]:
    # connect to the FTP server
    ftp = ftplib.FTP(timeout=30)
    ftp.connect(ftpHost, 21)
    time.sleep(2)
    ftp.login(ftpUname, ftpPass)
    time.sleep(2)
    if not (remoteWorkingDirectory == None or remoteWorkingDirectory.strip() == ""):
        _ = ftp.cwd(remoteWorkingDirectory)
        time.sleep(3)
    fnames = []
    try:
        fnames = ftp.nlst()
    except ftplib.error_perm as resp:
        if str(resp) == "550 No files found":
            fnames = []
        else:
            raise
    # quit and close the connection
    ftp.quit()

    return fnames

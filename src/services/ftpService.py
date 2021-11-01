import ftplib
import os
import time


def uploadFileToFtp(localFilePath: str, ftpHost: str, ftpUname: str, ftpPass: str, remoteWorkingDirectory: str) -> bool:
    isUploadSuccess: bool = False
    _, targetFilename = os.path.split(localFilePath)
    # connect to the FTP server
    ftp = ftplib.FTP(timeout=20)
    ftp.connect(ftpHost, 21)
    time.sleep(2)
    ftp.login(ftpUname, ftpPass)
    time.sleep(2)
    if not (remoteWorkingDirectory == None or remoteWorkingDirectory.strip() == ""):
        _ = ftp.cwd(remoteWorkingDirectory)
        time.sleep(3)

    # Read file in binary mode
    with open(localFilePath, "rb") as file:
        retCode = ftp.storbinary(f"STOR {targetFilename}", file, blocksize=1024*1024)
        time.sleep(2)

    # quit and close the connection
    ftp.quit()

    if retCode.startswith('226'):
        isUploadSuccess = True
    return isUploadSuccess


def downloadFileFromFtp(localFilePath: str, targetFilename: str, ftpHost: str, ftpUname: str, ftpPass: str, remoteWorkingDirectory: str) -> bool:
    isDownloadSuccess: bool = False
    # connect to the FTP server
    ftp = ftplib.FTP(timeout=10)
    ftp.connect(ftpHost, 21)
    time.sleep(2)
    ftp.login(ftpUname, ftpPass)
    time.sleep(2)
    if not (remoteWorkingDirectory == None or remoteWorkingDirectory.strip() == ""):
        _ = ftp.cwd(remoteWorkingDirectory)
        time.sleep(3)

    # Read file in binary mode
    with open(localFilePath, "wb") as file:
        retCode = ftp.retrbinary("RETR " + targetFilename, file.write)
        time.sleep(2)

    # quit and close the connection
    ftp.quit()

    if retCode.startswith('226'):
        isDownloadSuccess = True
    return isDownloadSuccess

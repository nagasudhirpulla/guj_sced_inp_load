import ftplib
import os
import time


def uploadFileToFtp(localFilePath: str, ftpHost: str, ftpUname: str, ftpPass: str, remoteWorkingDirectory: str) -> bool:
    isUploadSuccess: bool = False
    _, targetFilename = os.path.split(localFilePath)
    # connect to the FTP server
    ftp = ftplib.FTP(ftpHost, ftpUname, ftpPass)
    if not (remoteWorkingDirectory == None or remoteWorkingDirectory.strip() == ""):
        _ = ftp.cwd(remoteWorkingDirectory)
        time.sleep(1)

    # Read file in binary mode
    with open(localFilePath, "rb") as file:
        retCode = ftp.storbinary(f"STOR {targetFilename}", file)
        time.sleep(1)

    # quit and close the connection
    ftp.quit()

    if retCode.startswith('226'):
        isUploadSuccess = True
    return isUploadSuccess

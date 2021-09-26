import ftplib
import os


def uploadFileToFtp(localFilePath: str, ftpHost: str, ftpUname: str, ftpPass: str, remoteWorkingDirectory: str) -> bool:
    # TODO complete this
    _, targetFilename = os.path.split(localFilePath)
    # connect to the FTP server
    ftp = ftplib.FTP(ftpHost, ftpUname, ftpPass)
    if not (remoteWorkingDirectory == None or remoteWorkingDirectory.strip() == ""):
        ftp.cwd(remoteWorkingDirectory)

    # Read file in binary mode
    with open(localFilePath, "rb") as file:
        ftp.storbinary(f"STOR {targetFilename}", file)
    
    # quit and close the connection
    ftp.quit()
    return True

import datetime as dt
from typing import List
from src.app.filenames.fileTypes import ONBAR_FILE_TYPE, SCH_FILE_TYPE

from src.app.filenames.extractRevFromFname import extractRevFromFname
from src.typeDefs.csvInpFileInfo import ICsvFileInfo


def extractTargetDtFnames(fnames: List[str], targetDt: dt.datetime) -> List[ICsvFileInfo]:
    schFilePrefix = "Injection_Schedule_REVISION-"
    onbarFilePrefix = "Declared_Capacity_REVISION-"
    targetDtNameStr = dt.datetime.strftime(targetDt, '%d-%b-%Y').upper()
    targetFilesInfo: List[ICsvFileInfo] = []
    # check for required filenames to be downloaded from ftp location
    for fname in fnames:
        fType = None
        # check for valid file name prefixes
        if fname.startswith(schFilePrefix):
            fType = SCH_FILE_TYPE
        elif fname.startswith(onbarFilePrefix):
            fType = ONBAR_FILE_TYPE
        else:
            continue
        # check for valid date suffixes
        if not fname.lower().endswith("_"+targetDtNameStr.lower()+".csv"):
            continue
        # check if we have a valid revision number
        revNum = extractRevFromFname(fname)
        if revNum == None:
            continue
        targetFilesInfo.append({
            "name": fname,
            "fileType": fType,
            "revNum": revNum
        })
    return targetFilesInfo

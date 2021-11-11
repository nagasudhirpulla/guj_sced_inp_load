import datetime as dt
from typing import Optional


def extractTsFromRevInfoStr(revInfoStr: str) -> Optional[dt.datetime]:
    tsStartSearchStr = "_REVTIME-"
    tsEndSearchStr = ")"
    tsStartInd = revInfoStr.index(
        tsStartSearchStr)+len(tsStartSearchStr)
    tsEndInd = revInfoStr.index(tsEndSearchStr, tsStartInd)
    tsStr = revInfoStr[tsStartInd:tsEndInd]
    revTs = dt.datetime.strptime(tsStr, "%d-%b-%Y %H:%M:%S")
    return revTs

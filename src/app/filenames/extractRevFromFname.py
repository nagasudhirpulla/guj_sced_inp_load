from typing import Optional


def extractRevFromFname(fname: str) -> Optional[int]:
    revStartSearchStr = "revision-"
    revStartInd = fname.lower().index(revStartSearchStr)+len(revStartSearchStr)
    revEndInd = fname.index("_", revStartInd)
    revStr = fname[revStartInd:revEndInd]
    if not revStr.isdigit():
        return None
    else:
        return int(revStr)

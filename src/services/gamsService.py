from subprocess import Popen, PIPE, TimeoutExpired
import os


def runGams(gamsExePath: str, gamsCodePath: str, gamsLstPath: str) -> bool:
    isGamsExecutionSuccess = False
    (gamsCodeFolder, gamsCodeFileName) = os.path.split(gamsCodePath)

    if gamsCodeFolder.strip() == "":
        gamsCodeFolder = None

    proc = Popen([gamsExePath, gamsCodeFileName],
                 cwd=gamsCodeFolder, stdout=PIPE)
    try:
        _ = proc.communicate(timeout=15)
    except TimeoutExpired:
        proc.kill()

    # check if lst file is generated
    isGamsLstPresent = os.path.isfile(gamsLstPath)
    if isGamsLstPresent:
        # read lst content
        with open(gamsLstPath, mode='r') as f:
            # read all the file content
            gamsOutputStr = f.read()
            # check for success
            if (gamsOutputStr.count("**** SOLVER STATUS     1 Normal Completion") == 2) and (gamsOutputStr.count("**** MODEL STATUS      1 Optimal") == 2):
                isGamsExecutionSuccess = True
    return isGamsExecutionSuccess

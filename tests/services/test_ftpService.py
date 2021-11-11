import unittest
from src.services.ftpService import getFtpFilenames
from src.app.filenames.extractTargetDtFnames import extractTargetDtFnames
from src.config.appConfig import loadAppConfig
import datetime as dt


class TestFtpService(unittest.TestCase):
    appConf = {}

    def setUp(self):
        self.appConf = loadAppConfig()

    def test_getFtpFilenamesForDate(self) -> None:
        appConf = self.appConf
        remoteFilesDirectory = appConf["ftpFolderPath"]
        ftpHost = appConf["ftpHost"]
        ftpUname = appConf["ftpUname"]
        ftpPass = appConf["ftpPass"]
        fNames = getFtpFilenames(
            ftpHost, ftpUname, ftpPass, remoteFilesDirectory)
        self.assertFalse(len(fNames) == 0)
        # test the filenames filtering function
        targetDt = dt.datetime.now()
        revFilenames = extractTargetDtFnames(fNames, targetDt)
        self.assertFalse(len(revFilenames) == 0)

import unittest
from src.repos.latestRevData import LatestRevsRepo
from src.config.appConfig import loadAppConfig
import datetime as dt


class TestLatestRevDataRepo(unittest.TestCase):
    appConf = {}

    def setUp(self):
        self.appConf = loadAppConfig()

    def test_getLatestRevForDate(self) -> None:
        appConf = self.appConf
        dbHost = appConf["dbHost"]
        dbName = appConf["dbName"]
        dbUname = appConf["dbUname"]
        dbPass = appConf["dbPass"]
        latRevRepo = LatestRevsRepo(dbHost, dbName, dbUname, dbPass)
        latestRevInfo = latRevRepo.getLatestRevForDate(dt.datetime.now())
        self.assertFalse(latestRevInfo == None)

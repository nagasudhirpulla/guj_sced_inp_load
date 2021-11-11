import unittest
from src.repos.revsInfo import RevsInfoRepo
from src.config.appConfig import loadAppConfig
import datetime as dt


class TestRevsInfoRepo(unittest.TestCase):
    appConf = {}

    def setUp(self):
        self.appConf = loadAppConfig()

    def test_getLatestRevForDate(self) -> None:
        appConf = self.appConf
        dbHost = appConf["dbHost"]
        dbName = appConf["dbName"]
        dbUname = appConf["dbUname"]
        dbPass = appConf["dbPass"]
        revsInfoRepo = RevsInfoRepo(dbHost, dbName, dbUname, dbPass)
        latestRevInfo = revsInfoRepo.getMaxLocalRevObjForDate(
            dt.datetime.now())
        self.assertFalse(latestRevInfo == None)

    def test_getAllRevsForDate(self) -> None:
        appConf = self.appConf
        dbHost = appConf["dbHost"]
        dbName = appConf["dbName"]
        dbUname = appConf["dbUname"]
        dbPass = appConf["dbPass"]
        revsInfoRepo = RevsInfoRepo(dbHost, dbName, dbUname, dbPass)
        allRevs = revsInfoRepo.getAllRevsForDate(
            dt.datetime.now())
        self.assertFalse(len(allRevs) == 0)

import unittest
from src.app.filenames.extractTsFromRevInfoStr import extractTsFromRevInfoStr
import pandas as pd


class TestExtractRevTsFromRevInfoStr(unittest.TestCase):

    def test_case1(self) -> None:
        revTs = extractTsFromRevInfoStr("REVISION-9(SCHDATE-08-NOV-2021_REVTIME-08-NOV-2021 00:23:18)")
        self.assertFalse(pd.isna(revTs))

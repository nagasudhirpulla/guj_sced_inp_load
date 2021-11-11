import datetime as dt
from typing import List, Optional, Tuple

import psycopg2
from src.typeDefs.schRow import ISchRow
from src.typeDefs.latestRev import ILatestRev


class LatestRevsRepo():
    def __init__(self, dbHost: str, dbname: str, uname: str, dbPass: str) -> None:
        """constructor method
        Args:
            dbConf (DbConfig): database connection string
        """
        self.dbHost = dbHost
        self.dbname = dbname
        self.uname = uname
        self.dbPass = dbPass

    def getLatestRevForDate(self, targetDt: dt.datetime) -> Optional[ILatestRev]:
        latestRevInfo: Optional[ILatestRev] = None
        try:
            # get the connection object
            conn = psycopg2.connect(host=self.dbHost, dbname=self.dbname,
                                    user=self.uname, password=self.dbPass)
            # get the cursor from connection
            cur = conn.cursor()
            # create the query
            postgreSQL_select_Query = "SELECT id, rev_date, latest_guj_rev, latest_rev FROM public.daywise_latest_revs where rev_date = %s"

            # execute the query
            cur.execute(postgreSQL_select_Query, (dt.datetime(
                targetDt.year, targetDt.month, targetDt.day),))

            # fetch all the records from cursor
            records = cur.fetchall()

            # iterate through all the fetched records
            if not len(records) == 0:
                dbRow = records[0]
                latestRevInfo = {
                    "id": dbRow[0],
                    "revDt": dbRow[1],
                    "latestGujRev": dbRow[2],
                    "latestRev": dbRow[3]
                }
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
            latestRevInfo = None
        finally:
            # closing database connection and cursor
            if(conn):
                # close the cursor object to avoid memory leaks
                cur.close()
                # close the connection object also
                conn.close()
        return latestRevInfo

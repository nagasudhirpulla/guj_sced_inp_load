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

    def upsertLatestRevInfo(self, targetDt: dt.datetime, gujRevNum: int, rev: int):
        dbConn = None

        isInsertSuccess = True
        try:
            # get the connection object
            dbConn = psycopg2.connect(host=self.dbHost, dbname=self.dbname,
                                      user=self.uname, password=self.dbPass)
            # get cursor for raw data table
            dbCur = dbConn.cursor()

            # create sql for insertion
            dataInsertionTuples: List[Tuple] = [(dt.datetime.strftime(targetDt, "%Y-%m-%d %H:%M:%S"),
                                                gujRevNum, rev)]

            dataText = ','.join(dbCur.mogrify('(%s,%s,%s)', row).decode(
                "utf-8") for row in dataInsertionTuples)

            sqlTxt = 'INSERT INTO public.daywise_latest_revs(\
        	rev_date, latest_guj_rev, latest_rev)\
        	VALUES {0} on conflict (rev_date) \
            do update set latest_guj_rev = excluded.latest_guj_rev, latest_rev=excluded.latest_rev'.format(dataText)

            # execute the sql to perform insertion
            dbCur.execute(sqlTxt)

            # commit the changes
            dbConn.commit()
        except Exception as e:
            isInsertSuccess = False
            print('Error while bulk insertion of latest revision info into db')
            print(e)
        finally:
            # closing database connection and cursor
            if(dbConn):
                # close the cursor object to avoid memory leaks
                dbCur.close()
                # close the connection object also
                dbConn.close()
        return isInsertSuccess

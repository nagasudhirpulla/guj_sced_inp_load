import datetime as dt
from typing import List, Optional, Tuple

import psycopg2
from src.typeDefs.latestRev import ILatestRev
from src.typeDefs.revInfo import IRevInfoRecord


class RevsInfoRepo():
    def __init__(self, dbHost: str, dbname: str, uname: str, dbPass: str) -> None:
        self.dbHost = dbHost
        self.dbname = dbname
        self.uname = uname
        self.dbPass = dbPass

    def getGujRevInfo(self, targetDt: dt.datetime, gujRevNum: int) -> Optional[IRevInfoRecord]:
        revInfo: Optional[IRevInfoRecord] = None
        try:
            # get the connection object
            conn = psycopg2.connect(host=self.dbHost, dbname=self.dbname,
                                    user=self.uname, password=self.dbPass)
            # get the cursor from connection
            cur = conn.cursor()
            # create the query
            postgreSQL_select_Query = "SELECT id, rev_date, rev_num, rev_time FROM public.revs_info where rev_date = %s and guj_rev=%s"

            # execute the query
            cur.execute(postgreSQL_select_Query, (dt.datetime(
                targetDt.year, targetDt.month, targetDt.day), gujRevNum))

            # fetch all the records from cursor
            records = cur.fetchall()

            # iterate through all the fetched records
            if not len(records) == 0:
                dbRow = records[0]
                revInfo = {
                    "id": dbRow[0],
                    "revDt": dbRow[1],
                    "rev": dbRow[2],
                    "revTs": dbRow[3],
                    "gujRev": gujRevNum
                }
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
            revInfo = None
        finally:
            # closing database connection and cursor
            if(conn):
                # close the cursor object to avoid memory leaks
                cur.close()
                # close the connection object also
                conn.close()
        return revInfo

    def getMaxLocalRevObjForDate(self, targetDt: dt.datetime) -> Optional[IRevInfoRecord]:
        revInfo: Optional[IRevInfoRecord] = None
        try:
            # get the connection object
            conn = psycopg2.connect(host=self.dbHost, dbname=self.dbname,
                                    user=self.uname, password=self.dbPass)
            # get the cursor from connection
            cur = conn.cursor()
            # create the query
            postgreSQL_select_Query = "SELECT id, rev_date, guj_rev, rev_num, rev_time FROM public.revs_info where rev_date = %s and rev_num in (select max(rev_num) from public.revs_info where rev_date = %s)"

            # execute the query
            cur.execute(postgreSQL_select_Query, (dt.datetime(targetDt.year, targetDt.month,
                        targetDt.day), dt.datetime(targetDt.year, targetDt.month, targetDt.day)))

            # fetch all the records from cursor
            records = cur.fetchall()

            # iterate through all the fetched records
            if not len(records) == 0:
                dbRow = records[0]
                revInfo = {
                    "id": dbRow[0],
                    "revDt": dbRow[1],
                    "gujRev": dbRow[2],
                    "rev": dbRow[3],
                    "revTs": dbRow[4]
                }
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
            revInfo = None
        finally:
            # closing database connection and cursor
            if(conn):
                # close the cursor object to avoid memory leaks
                cur.close()
                # close the connection object also
                conn.close()
        return revInfo

    def getAllRevsForDate(self, targetDt: dt.datetime) -> List[IRevInfoRecord]:
        revs: List[IRevInfoRecord] = []
        try:
            # get the connection object
            conn = psycopg2.connect(host=self.dbHost, dbname=self.dbname,
                                    user=self.uname, password=self.dbPass)
            # get the cursor from connection
            cur = conn.cursor()
            # create the query
            postgreSQL_select_Query = "SELECT id, rev_date, guj_rev, rev_num, rev_time FROM public.revs_info where rev_date = %s order by rev_num"

            # execute the query
            cur.execute(postgreSQL_select_Query, (dt.datetime(
                targetDt.year, targetDt.month, targetDt.day),))

            # fetch all the records from cursor
            records = cur.fetchall()

            # iterate through all the fetched records
            for rItr in range(len(records)):
                dbRow = records[rItr]
                revInfo: IRevInfoRecord = {
                    "id": dbRow[0],
                    "revDt": dbRow[1],
                    "gujRev": dbRow[2],
                    "rev": dbRow[3],
                    "revTs": dbRow[4]
                }
                revs.append(revInfo)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
            revs = []
        finally:
            # closing database connection and cursor
            if(conn):
                # close the cursor object to avoid memory leaks
                cur.close()
                # close the connection object also
                conn.close()
        return revs

    def insertRevInfo(self, targetDt: dt.datetime, gujRevNum: int, rev: int, revTs: dt.datetime):
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
                                                gujRevNum, rev, dt.datetime.strftime(revTs, "%Y-%m-%d %H:%M:%S"))]

            dataText = ','.join(dbCur.mogrify('(%s,%s,%s,%s)', row).decode(
                "utf-8") for row in dataInsertionTuples)

            sqlTxt = 'INSERT INTO public.revs_info(\
        	rev_date, guj_rev, rev_num, rev_time)\
        	VALUES {0}'.format(dataText)

            # execute the sql to perform insertion
            dbCur.execute(sqlTxt)

            # commit the changes
            dbConn.commit()
        except Exception as e:
            isInsertSuccess = False
            print('Error while bulk insertion of revisions info into db')
            print(e)
        finally:
            # closing database connection and cursor
            if(dbConn):
                # close the cursor object to avoid memory leaks
                dbCur.close()
                # close the connection object also
                dbConn.close()
        return isInsertSuccess

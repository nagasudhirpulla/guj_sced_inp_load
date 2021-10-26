import datetime as dt
from typing import List, Tuple

import psycopg2
from src.typeDefs.smpRow import ISmpRow


class SmpRepo():
    def __init__(self, dbHost: str, dbname: str, uname: str, dbPass: str) -> None:
        self.dbHost = dbHost
        self.dbname = dbname
        self.uname = uname
        self.dbPass = dbPass

    def insertSmp(self, smpRows: List[ISmpRow]) -> bool:
        dbConn = None

        isInsertSuccess = True
        try:
            # get the connection object
            dbConn = psycopg2.connect(host=self.dbHost, dbname=self.dbname,
                                      user=self.uname, password=self.dbPass)
            # get cursor for raw data table
            dbCur = dbConn.cursor()

            # create sql for insertion
            dataInsertionTuples: List[Tuple] = [(x["regTag"], dt.datetime.strftime(x["dataTime"], "%Y-%m-%d %H:%M:%S"),
                                                 x["smpVal"], x["rev"]) for x in smpRows]

            dataText = ','.join(dbCur.mogrify('(%s,%s,%s,%s)', row).decode(
                "utf-8") for row in dataInsertionTuples)

            sqlTxt = 'INSERT INTO public.smp_data(\
        	region_tag, data_time, smp_val, rev)\
        	VALUES {0} on conflict (region_tag, data_time, rev) \
            do update set smp_val = excluded.smp_val'.format(dataText)

            # execute the sql to perform insertion
            dbCur.execute(sqlTxt)

            # commit the changes
            dbConn.commit()
        except Exception as e:
            isInsertSuccess = False
            print('Error while bulk insertion of SMP values into db')
            print(e)
        finally:
            # closing database connection and cursor
            if(dbConn):
                # close the cursor object to avoid memory leaks
                dbCur.close()
                # close the connection object also
                dbConn.close()
        return isInsertSuccess

    def getSmp(self, regTag: str, revisionNum: int, startTime: dt.datetime, endTime: dt.datetime) -> List[ISmpRow]:
        smpObjs: List[ISmpRow] = []
        try:
            # get the connection object
            conn = psycopg2.connect(host=self.dbHost, dbname=self.dbname,
                                    user=self.uname, password=self.dbPass)
            # get the cursor from connection
            cur = conn.cursor()
            # create the query
            postgreSQL_select_Query = "select data_time, smp_val from public.smp_data where region_tag=%s and rev=%s and (data_time between %s and %s) order by data_time"

            # execute the query
            cur.execute(postgreSQL_select_Query,
                        (regTag, revisionNum, startTime, endTime))

            # fetch all the records from cursor
            records = cur.fetchall()

            # iterate through all the fetched records
            for rowIter in range(len(records)):
                dbRow = records[rowIter]
                smpObj: ISmpRow = {
                    "dataTime": dbRow[0],
                    "smpVal": dbRow[1],
                    "regTag": regTag,
                    "rev": revisionNum
                }
                smpObjs.append(smpObj)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
            smpObjs = []
        finally:
            # closing database connection and cursor
            if(conn):
                # close the cursor object to avoid memory leaks
                cur.close()
                # close the connection object also
                conn.close()
        return smpObjs

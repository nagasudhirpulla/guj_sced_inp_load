import datetime as dt
from typing import List, Tuple

import psycopg2
from src.typeDefs.schRow import ISchRow


class SchedulesRepo():
    """Repository class for outages data of application
    """

    def __init__(self, dbHost: str, dbname: str, uname: str, dbPass: str) -> None:
        """constructor method
        Args:
            dbConf (DbConfig): database connection string
        """
        self.dbHost = dbHost
        self.dbname = dbname
        self.uname = uname
        self.dbPass = dbPass

    def insertSchedules(self, schRows: List[ISchRow]) -> bool:
        dbConn = None

        isInsertSuccess = True
        try:
            # get the connection object
            dbConn = psycopg2.connect(host=self.dbHost, dbname=self.dbname,
                                      user=self.uname, password=self.dbPass)
            # get cursor for raw data table
            dbCur = dbConn.cursor()

            # create sql for insertion
            dataInsertionTuples: List[Tuple] = [(x["genId"], x["schType"], dt.datetime.strftime(x["schTime"], "%Y-%m-%d %H:%M:%S"),
                                                x["schVal"], x["rev"]) for x in schRows]

            dataText = ','.join(dbCur.mogrify('(%s,%s,%s,%s,%s)', row).decode(
                "utf-8") for row in dataInsertionTuples)

            sqlTxt = 'INSERT INTO public.gens_data(\
        	g_id, sch_type, sch_time, sch_val, rev)\
        	VALUES {0} on conflict (g_id, sch_type, sch_time, rev) \
            do update set sch_val = excluded.sch_val'.format(dataText)

            # execute the sql to perform insertion
            dbCur.execute(sqlTxt)

            # commit the changes
            dbConn.commit()
        except Exception as e:
            isInsertSuccess = False
            print('Error while bulk insertion of generator schedules into db')
            print(e)
        finally:
            # closing database connection and cursor
            if(dbConn):
                # close the cursor object to avoid memory leaks
                dbCur.close()
                # close the connection object also
                dbConn.close()
        return isInsertSuccess

    def getGenSchedules(self, schType: str, genId: int, revisionNum: int, startTime: dt.datetime, endTime: dt.datetime) -> List[ISchRow]:
        schObjs: List[ISchRow] = []
        try:
            # get the connection object
            conn = psycopg2.connect(host=self.dbHost, dbname=self.dbname,
                                    user=self.uname, password=self.dbPass)
            # get the cursor from connection
            cur = conn.cursor()
            # create the query
            postgreSQL_select_Query = "select sch_time, sch_val from public.gens_data where sch_type=%s and g_id=%s and rev=%s and (sch_time between %s and %s) order by sch_time"

            # execute the query
            cur.execute(postgreSQL_select_Query,
                        (schType, genId, revisionNum, startTime, endTime))

            # fetch all the records from cursor
            records = cur.fetchall()

            # iterate through all the fetched records
            for rowIter in range(len(records)):
                dbRow = records[rowIter]
                schObj: ISchRow = {
                    "schTime": dbRow[0],
                    "schVal": dbRow[1],
                    "genId": genId,
                    "schType": schType,
                    "rev": revisionNum
                }
                schObjs.append(schObj)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
            schObjs = []
        finally:
            # closing database connection and cursor
            if(conn):
                # close the cursor object to avoid memory leaks
                cur.close()
                # close the connection object also
                conn.close()
        return schObjs

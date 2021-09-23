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

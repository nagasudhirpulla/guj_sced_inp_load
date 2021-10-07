import datetime as dt
from typing import List, Tuple

import psycopg2
from src.typeDefs.dailyDataRow import IDailyDataRow


class DailyDataRepo():
    def __init__(self, dbHost: str, dbname: str, uname: str, dbPass: str) -> None:
        """constructor method
        Args:
            dbConf (DbConfig): database connection string
        """
        self.dbHost = dbHost
        self.dbname = dbname
        self.uname = uname
        self.dbPass = dbPass

    def insertRows(self, dataRows: List[IDailyDataRow]) -> bool:
        dbConn = None

        isInsertSuccess = True
        try:
            # get the connection object
            dbConn = psycopg2.connect(host=self.dbHost, dbname=self.dbname,
                                      user=self.uname, password=self.dbPass)
            # get cursor for raw data table
            dbCur = dbConn.cursor()

            # create sql for insertion
            dataInsertionTuples: List[Tuple] = [(x["genId"], x["dataType"], dt.datetime.strftime(x["targetDt"], "%Y-%m-%d"),
                                                x["dataVal"], 0) for x in dataRows]

            dataText = ','.join(dbCur.mogrify('(%s,%s,%s,%s,%s)', row).decode(
                "utf-8") for row in dataInsertionTuples)

            sqlTxt = 'INSERT INTO public.gens_daily_data(\
        	g_id, data_type, data_date, data_val, rev)\
        	VALUES {0} on conflict (g_id, data_type, data_date, rev) \
            do update set data_val = excluded.data_val'.format(dataText)

            # execute the sql to perform insertion
            dbCur.execute(sqlTxt)

            # commit the changes
            dbConn.commit()
        except Exception as e:
            isInsertSuccess = False
            print('Error while bulk insertion of generator daily data into db')
            print(e)
        finally:
            # closing database connection and cursor
            if(dbConn):
                # close the cursor object to avoid memory leaks
                dbCur.close()
                # close the connection object also
                dbConn.close()
        return isInsertSuccess

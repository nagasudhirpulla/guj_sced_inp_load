from typing import Dict
from numpy import number

import psycopg2


class GensMasterRepo():
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

    def getGenIds(self) -> Dict[str, number]:
        genIdsDict: Dict[str, number] = {}
        try:
            # get the connection object
            conn = psycopg2.connect(host=self.dbHost, dbname=self.dbname,
                                    user=self.uname, password=self.dbPass)
            # get the cursor from connection
            cur = conn.cursor()
            # create the query
            postgreSQL_select_Query = "select id, g_name from public.gens order by g_name"

            # execute the query
            cur.execute(postgreSQL_select_Query)

            # fetch all the records from cursor
            records = cur.fetchall()

            # iterate through all the fetched records
            for rowIter in range(len(records)):
                dbRow = records[rowIter]
                gId = dbRow[0]
                gName = dbRow[1]
                genIdsDict[gName] = gId
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
            genIdsDict = {}
        finally:
            # closing database connection and cursor
            if(conn):
                # close the cursor object to avoid memory leaks
                cur.close()
                # close the connection object also
                conn.close()
        return genIdsDict

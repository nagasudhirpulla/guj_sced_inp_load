from typing import Dict, List

import psycopg2
from src.typeDefs.genObj import IGenObj


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

    def getGenIds(self) -> Dict[str, int]:
        genIdsDict: Dict[str, int] = {}
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

    def getGens(self) -> List[IGenObj]:
        gens: List[IGenObj] = []
        try:
            # get the connection object
            conn = psycopg2.connect(host=self.dbHost, dbname=self.dbname,
                                    user=self.uname, password=self.dbPass)
            # get the cursor from connection
            cur = conn.cursor()
            # create the query
            postgreSQL_select_Query = "select id, g_name, vc, fuel_type, avg_pu_cap, tm_pu, rup_pu, rdn_pu from public.gens order by g_name"

            # execute the query
            cur.execute(postgreSQL_select_Query)

            # fetch all the records from cursor
            records = cur.fetchall()

            # iterate through all the fetched records
            for rowIter in range(len(records)):
                dbRow = records[rowIter]
                genObj: IGenObj = {
                    "id": dbRow[0],
                    "name": dbRow[1],
                    "vcPu": dbRow[2],
                    "fuelType": dbRow[3],
                    "capPu": dbRow[4],
                    "tmPu": dbRow[5],
                    "rUpPu": dbRow[6],
                    "rDnPu": dbRow[7],
                }
                gens.append(genObj)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
            gens = []
        finally:
            # closing database connection and cursor
            if(conn):
                # close the cursor object to avoid memory leaks
                cur.close()
                # close the connection object also
                conn.close()
        return gens

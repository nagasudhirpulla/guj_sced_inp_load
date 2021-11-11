# guj_sced_inp_load
loads the input data for gujarat sced into database

## Script 1 - Data files fetch
* Reads the data files for the target dates from FTP location and pastes in the input data folder

## Script 2 - Data Load into DB from files
* Reads the data files for the target dates from folder location and loads the data into the database

## Script 3 - Data into GAMS excel and push results to DB
* Reads the data from db for a target date and populates the input excel file, runs the optimization and saves the output to db

## Script 4 - Publish input and results data to ftp location
* Reads input and output data from db, creates excel file and stores it in a local dumps folder and a remote ftp location 

## checks in input data loading to db script
* check if relevant ON-BAR DC file is present
* check if relevant Schedule file is present       
* check if all generators are present in onbar file
* check if onbar data of input csv has 96 rows     
* check if schedule data of input csv has 96 rows  
* check if all on bar gens are present in sch df

## checks in gams code execution script
* check if gams excel file exists
* if onbar data sheet of gams input excel file exists
* if schedule data sheet of gams input excel file exists
* check if gams execution is successful
* if gams excel results sheet of gams input excel file exists
* check if gams excel result sheet was populated with at least 98 blocks
* check if the gams excel result sheet was populated with all 96 blocks
* check if all the database generators are present in the gams excel result sheet 

## sample file names
* Injection_Schedule_REVISION-15_31-OCT-2021.csv
* Declared_Capacity_REVISION-7_01-NOV-2021.csv

## algorithm for real time revision-based input data import into database
* date-wise latest processed revisions will be tracked in a table with the columns date, latest guj rev, latest rev ((date, latest rev) and (date, guj rev) will be unique)
* All revisions will be tracked in a table with columns date, guj rev, rev, revision timestamp ((date, rev) and (date, guj rev) will be unique)
* If no revision is specified, then we will search for all the files that contain data for (latest_revision+1) revision in ftp location, process the data, update the latest revisions and processed revisions tables, publish results
* If specific revision is specified, then we will search only for that file in ftp location, process the data, update the latest revisions and processed revisions tables, publish results

## Useful Links
* ftp folder directory listing - https://stackoverflow.com/questions/111954/using-pythons-ftplib-to-get-a-directory-listing-portably
* change directory in ftp - https://stackoverflow.com/a/43718818

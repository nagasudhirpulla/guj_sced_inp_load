@REM https://stackoverflow.com/questions/1192476/format-date-and-time-in-a-windows-batch-script
@REM https://stackoverflow.com/questions/21809027/batch-file-run-cmd1-if-time-10pm-4am-else-run-cmd2
@REM https://stackoverflow.com/questions/25166704/convert-a-string-to-integer-in-a-batch-file
call .\activate_env.bat

call python index_fetch_ftp_files.py
call python index_load_from_folder.py
call python index_run_gams_from_excel.py
call python index_publish_results_to_excel.py

@REM derive the current time in HHMM formatted string
set hour=%time:~0,2%
if "%hour:~0,1%" == " " set hour=0%hour:~1,1%
set min=%time:~3,2%
if "%min:~0,1%" == " " set min=0%min:~1,1%
set time_f=%hour%%min%
@REM echo current time is %time_f%

if "%time_f%" geq "1900" ( 
    @REM perform day ahead optimization also if time greater than 1900 hrs
    call python index_fetch_ftp_files.py --doff 1
    call python index_load_from_folder.py --doff 1
    call python index_run_gams_from_excel.py --doff 1
    call python index_publish_results_to_excel.py --doff 1
)
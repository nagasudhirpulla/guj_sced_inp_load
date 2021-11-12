call .\activate_env.bat
for /l %%A in (12, 1, 12) do (
call python index_fetch_ftp_files.py --date=2021-11-%%A
call python index_load_from_folder.py --date=2021-11-%%A
call python index_run_gams_from_excel.py --date=2021-11-%%A
@REM call python index_publish_results_to_excel.py --date=2021-11-%%A
)
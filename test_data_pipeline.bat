call .\activate_env.bat
FOR /L %%A IN (1,1,2) DO (
    call python index_fetch_ftp_files.py --date=2021-12-0%%A
    call python index_load_from_folder.py --date=2021-12-0%%A
    call python index_run_gams_from_excel.py --date=2021-12-0%%A
    call python index_publish_results_to_excel.py --date=2021-12-0%%A
)
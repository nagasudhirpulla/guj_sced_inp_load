call .\activate_env.bat
call python index_load_from_folder.py --date 2021-09-17
call python index_run_gams_from_excel.py --date 2021-09-17
call python index_publish_results_to_excel.py --date 2021-09-17
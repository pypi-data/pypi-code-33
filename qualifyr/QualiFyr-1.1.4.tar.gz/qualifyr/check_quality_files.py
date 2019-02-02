def check_all_quality_files(conditions, quality_files):
    all_pass = True
    for quality_file in quality_files:

        result = quality_file.check(conditions)
        if not result:
            all_pass = False
    # write to log file 
    # format
    # file_type    metric    value    condition    pass/fail
    print(all_pass)

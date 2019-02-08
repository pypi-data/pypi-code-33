import time
import os
import json
import subprocess
from datetime import datetime


def set_bginfo(
        path_bginfo_exe,
        path_bginfo_config_file,
        int_bginfo_timer=0
):
    return subprocess.Popen(
        [path_bginfo_exe, path_bginfo_config_file, r"/timer:{:d}".format(int_bginfo_timer)],
        stderr=subprocess.STDOUT, stdout=subprocess.PIPE
    )


def bginfo():

    path_fds_queue_file = os.path.join('C:', os.sep, 'APP', 'fdspy', 'fds_queue.json')
    path_bginfo_exe = os.path.join('C:', os.sep, 'app', 'bginfo', 'bginfo.exe')
    path_bginfo_config_file = os.path.join('C:', os.sep, 'app', 'bginfo', 'bginfo_config.bgi')
    path_bginfo_config_text = os.path.join('C:', os.sep, 'app', 'bginfo', 'bginfo_text')

    table_header_fmt = "{uid:7.7}{user:10.10}{datetime_start:16.16}{path_fds:30.30}{num_omp:7.7}{num_mpi:7.7}{progress:11.11}{status:6.6}\n"
    table_content_fmt = "{uid:<7.7}{user:<10.6}{datetime_start:16.12}{path_fds:<30.26}{num_omp:<7d}{num_mpi:<7d}{progress:<11.1f}{status:<6d}\n"

    table_top_boarder = "=" * (7 + 10 + 16 + 30 + 7 + 7 + 11 + 6) + "\n"
    table_top_boarder2 = table_top_boarder.replace('=', '-')
    table_header = table_header_fmt.format(uid="UID", user="User", datetime_start="Start Time", path_fds="Job Name",
        num_omp="OMP", num_mpi="MPI", progress="Progress", status="Status")
    table_bottom_boarder = table_top_boarder.replace("\n", "")

    table_container = table_top_boarder + table_header + table_top_boarder2 + "{table_content}" + table_bottom_boarder


    while True:

        with open(path_fds_queue_file, "r") as f:
            dict_queue = json.load(f)

        table_content = ""
        if len(dict_queue) > 0:
            for uid, v in dict_queue.items():
                if v["status"]==0 or v["status"]==1:
                    v["path_fds"] = v["path_fds"][-26:]
                    v["datetime_start"] = datetime.strftime(datetime.strptime(v["datetime_start"], "%Y-%m-%d %H:%M:%S"), "%y%m%d %H:%M")
                    table_content += table_content_fmt.format(uid=uid, **v)
        if len(table_content) == 0:
            table_content = "Empty\n"

        with open(path_bginfo_config_text, 'w') as f:
            f.write(table_container.format(table_content=table_content))

        set_bginfo(
            path_bginfo_exe=path_bginfo_exe,
            path_bginfo_config_file=path_bginfo_config_file
        )

        time.sleep(30)

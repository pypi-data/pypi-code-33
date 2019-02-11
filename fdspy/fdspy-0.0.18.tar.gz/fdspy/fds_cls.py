# -*- coding: utf-8 -*-
import copy
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time

import collections
import pprint

class FdsJob(object):
    def __init__(
            self, uid, path_fds, user=None, num_mpi=1, num_omp=1, path_destination=None, status=0,
            **red_kwargs,
    ):

        # HIDDEN VARIABLES

        self._uid = ''
        self._fds_str = ''
        self._fds_chid = ''
        self._fds_uptime = 0
        self._current_progress = 0

        # ASSIGN USER DEFINED PROPERTIES

        self.uid = uid
        self.path_fds = os.path.realpath(path_fds)
        self.user = user
        self.num_mpi = int(num_mpi)
        self.num_omp = int(num_omp)
        self.status = int(status)
        self.path_destination = path_destination
        self.path_work = os.path.dirname(self.path_fds)

        # ASSIGN PROPERTIES

        self.fds_str = self.path_fds
        self.chid = self._fds_str
        self.uptime = self._fds_str

        self.sp = None

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, v):
        self._uid = v

    @property
    def chid(self):
        return self._fds_chid

    @chid.setter
    def chid(self, str_fds):
        self._fds_chid = \
            re.compile("'[\S]+'").search(
                re.compile('CHID=[\s\S]+?[/,]').search(
                    re.compile("&HEAD[\s\S]*?/").search(
                        str_fds
                    ).group(0)
                ).group(0)
            ).group(0).replace("'", '')

    @property
    def uptime(self):
        return self._fds_uptime

    @uptime.setter
    def uptime(self, str_fds):
        self._fds_uptime = \
            float(
                re.compile("[\d.]+").search(
                    re.compile("T_END=[\s\S\d.]*?[,/]").search(
                        re.compile("&TIME[\s\S]*?/").search(
                            str_fds
                        ).group(0)
                    ).group(0)
                ).group(0)
            )

    @property
    def fds_str(self):
        return self._fds_str

    @fds_str.setter
    def fds_str(self, path_fds):
        with open(path_fds, 'r') as f:
            self._fds_str = f.read()

    def run(self):

        os.chdir(self.path_work)
        os.environ['OMP_NUM_THREADS'] = '{:d}'.format(self.num_omp)

        if self.num_mpi <= 1:
            str_cmd = 'fds {}'.format(os.path.basename(self.path_fds))
        else:
            str_cmd = 'mpiexec -localonly -n {:d} fds "{}"'.format(self.num_mpi, os.path.basename(self.path_fds))

        self.sp = subprocess.Popen(
            args=str_cmd,
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=self.path_work,
            bufsize=1,
            close_fds='posix' in sys.builtin_module_names
        )

    def check_is_live(self):

        # check subprocess status
        if self.sp.poll() is None:
            return True
        else:
            return False

    def get_current_progress(self):

        path_out_file = os.path.join(self.path_work, '{}.out'.format(self._fds_chid))

        try:
            with open(path_out_file, 'r') as f:
                str_out_file = f.read()
        except FileNotFoundError:
            str_out_file = ''

        try:
            self._current_progress = float(
                re.compile('[\d.]+').findall(
                    re.compile('Total Time:[\s\S\d.]+?s').findall(
                        str_out_file
                    )[-1]
                )[-1]
            )
        except IndexError:
            pass

        return self._current_progress

    def move_files(self):
        if self.path_destination:
            shutil.copytree(self.path_work, os.path.join(self.path_destination, os.path.basename(self.path_work)))
            time.sleep(0.5)
            shutil.rmtree(self.path_work, ignore_errors=True)
            time.sleep(0.5)


class ClientAgentBack(object):
    def __init__(self, path_fds_queue, available_cpu_cores, auto_start=True):

        self.path_fds_queue_json = path_fds_queue
        self.count_cpu_cores_available = available_cpu_cores

        self._count_live_jobs = 0
        self._count_cpu_cores_used = 0
        self._list_FdsJob = []

        if auto_start:
            self.start()

    def start(self, time_wait=30.):

        while True:
            self.update_queue_progress()

            # CHECK CPU USAGE
            if (self.count_cpu_cores_available - self._count_cpu_cores_used) <= 0:
                time.sleep(time_wait)
                continue

            # READ FDS QUEUE
            fds_queue_pending_due = self.queue_status(self.queue_read(), 0)
            fds_queue_pending_due = self.queue_datetime_due(fds_queue_pending_due, datetime.datetime.now())
            if len(fds_queue_pending_due) == 0:
                time.sleep(time_wait)
                continue

            # CHECK NEXT IN QUEUE
            fds_job_config_key_next = sorted(fds_queue_pending_due.keys())[0]
            fds_job_config = fds_queue_pending_due[fds_job_config_key_next]

            # RUN FDS JOB IF ENOUGH RESOURCE
            count_pt = fds_job_config['num_omp'] * fds_job_config['num_mpi']
            count_cpu_available = self.count_cpu_cores_available - self._count_cpu_cores_used
            if count_cpu_available >= count_pt:
                self.print("Job started UID {} ...".format(fds_job_config_key_next))
                # QUEUE FDS
                j = FdsJob(uid=fds_job_config_key_next, **fds_job_config)
                j.run()
                self._list_FdsJob.append(j)
                self.update_queue_json(j._uid, status=1)

            time.sleep(time_wait)

    def queue_read(self):
        with open(self.path_fds_queue_json, 'r') as f:
            return collections.OrderedDict(sorted(json.load(f).items()))

    def queue_write(self, dict):
        with open(self.path_fds_queue_json, 'w') as f:
            json.dump(dict, f, indent=4)

    def update_queue_json(self, uid, **job_params):
        queue = self.queue_read()

        # UPDATE JOB, IF GIVEN
        if uid in queue:
            for k, v in job_params.items():
                queue[uid][k] = v

        self.queue_write(queue)

    def update_queue_progress(self):
        dict_queue = self.queue_read()
        count_pt = 0

        # Check for complete/killed jobs; update progress
        for i, FdsJob in enumerate(self._list_FdsJob):
            dict_queue[FdsJob.uid]['progress'] = FdsJob.get_current_progress()

            if FdsJob.check_is_live():

                if dict_queue[FdsJob.uid]["status"] == 4:
                    FdsJob.sp.kill()
                    self.print('Job killed UID {} ...'.format(FdsJob.uid))
                    del self._list_FdsJob[i]
                else:
                    count_pt += (FdsJob.num_omp * FdsJob.num_mpi)

            else:

                self.print('Job complete UID {} ...'.format(FdsJob.uid))
                dict_queue[FdsJob.uid]['status'] = 2
                FdsJob.move_files()
                del self._list_FdsJob[i]

        self._count_live_jobs = len(self._list_FdsJob)
        self._count_cpu_cores_used = count_pt
        self._count_cpu_cores_used = sum([Job.num_omp * Job.num_mpi for Job in self._list_FdsJob])

        self.queue_write(dict_queue)

    @staticmethod
    def queue_status(dict_queue, status):
        q = dict_queue
        q_ = copy.copy(q)
        for k, v in q.items():
            if v['status'] != status:
                del q_[k]
        return q_

    @staticmethod
    def queue_datetime_due(dict_queue, datetime_obj):
        q_ = copy.copy(dict_queue)
        for k, v in dict_queue.items():
            if datetime_obj < datetime.datetime.strptime(v['datetime_start'], "%Y-%m-%d %H:%M:%S"):
                del q_[k]
        return q_

    @staticmethod
    def print(msg):
        pprint.pprint(msg)


class ClientAgentFront(object):
    def __init__(self, path_fds_queue, auto_start=True):
        self.path_fds_queue = path_fds_queue

        if auto_start:
            self.start()

    def start(self):
        while True:
            cmd = input(">>>")

            if cmd == "exit":
                break
            elif cmd == "append":
                self.queue_write(self.queue_append())
            elif cmd == "kill":
                self.queue_kill(input("UID: "))
            elif cmd == "help":
                print("append, kill")
            else:
                print("Unknown command.")

    def queue_append(self):
        dict_queue = self.queue_read()
        if len(dict_queue) > 0:
            uid = "{:d}".format(int(list(dict_queue)[-1]) + 1)
        else:
            uid = 0

        dict_queue[uid] = {}
        dict_queue[uid]["path_fds"] = self._input_path("Drop *.fds file: ")
        dict_queue[uid]["user"] = input("User initials: ")
        dict_queue[uid]["num_omp"] = int(input("Number of OMP threads: "))
        dict_queue[uid]["num_mpi"] = int(input("Number of MPI processes: "))
        dict_queue[uid]["datetime_start"] = self._input_datetime(
            "Date and time to start simulation (e.g. 2019-01-31 23:59:59, can be empty): ", "%Y-%m-%d %H:%M:%S")
        dict_queue[uid]["progress"] = 0
        dict_queue[uid]["status"] = 0
        dict_queue[uid]["path_destination"] = self._input_path("Drop destination folder (can be empty): ")

        return dict_queue

    def queue_delete(self, uid):
        dict_queue = self.queue_read()
        if uid in dict_queue:
            if dict_queue[uid]['status'] == 0:
                del dict_queue[uid]
            else:
                print("Deletion unsuccessful - job status is not pending")
        else:
            print("Deletion unsuccessful - unable to find UID")

    def queue_insert(self):
        pass

    def queue_kill(self, uid):
        dict_queue = self.queue_read()
        try:
            dict_queue[uid]['status'] = 4
            self.queue_write(dict_queue)
            print("Kill/deletion successful.")
        except KeyError:
            print("UID does not exist.")

    def queue_read(self):
        with open(self.path_fds_queue, "r") as f:
            # dict_queue = json.load(f)
            return collections.OrderedDict(sorted(json.load(f).items()))

    def queue_write(self, str):
        with open(self.path_fds_queue, "w") as f:
            json.dump(str, f, indent=4)

    @staticmethod
    def _input_path(msg):
        r = input(msg)
        if len(r) == 0:
            return None
        elif r[0] == r[-1] == '"' or r[0] == r[-1] == "'":
            return os.path.realpath(r[1:-1])
        else:
            return os.path.realpath(r)

    @staticmethod
    def _input_datetime(msg, fmt):
        while True:
            r = input(msg)

            if len(r) == 0:
                return datetime.datetime.strftime(datetime.datetime.now(), fmt)
            else:
                try:
                    datetime.datetime.strptime(r, fmt)
                    return r
                except ValueError:
                    print("Incorrect data format, try again.")


if __name__ == '__main__':
    # CA = ClientAgentBack(
    #     path_fds_queue=r"C:\Users\ian\Desktop\fdspy_test\fds_batch.json",
    #     available_cpu_cores=4
    # )
    # CA.start(time_wait=1)

    # CAF = ClientAgentFront(
    #     path_fds_queue=r"C:\Users\IanFu\Desktop\fdspy_test\fds_queue.json"
    # )
    # CAF.start()

    a = FdsJob(uid='0',path_fds=r"C:\Users\IanFu\Desktop\fdspy_test\job3\job.fds")
    print(a.uid)

    pass

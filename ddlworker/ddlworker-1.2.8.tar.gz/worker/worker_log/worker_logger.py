# verbosity level
# 0: error
# 1: warning
# 2: info
# 3: debug
import pymysql
from common.log_commons import *


class worker_logger(object):
    pid = None
    worker_id = None
    worker_type = None
    resource_id = None
    conn = None

    def __init__(self,
                 pid,
                 logdir,
                 worker_id="<none>",
                 worker_type="<none>",
                 resource_id=-1):

        self.pid = pid
        self.logdir = logdir
        self.worker_id = worker_id
        self.worker_type = worker_type
        self.resource_id = resource_id

    def commit_log(self, event, message, task_id, level):
        if not COMMIT_LOG:
            return

        # If the worker cannot be idenitifed, do not bother commit the log to DB as it is
        # useless.
        if self.worker_id == "<none>":
            return

        assert level is not None
        assert event is not None

        if self.conn is None or not self.conn.open:
            self.conn = pymysql.connect(host=hostname, user=username, passwd=password, db=database)

        cur = self.conn.cursor()
        query = "INSERT INTO tbl_worker_log " \
                "(pid, timestamp, worker_id, worker_type, resource_id, level, task_id, event, message)" \
                " VALUES ({}, NOW(4), {}, {}, {}, {}, {}, {}, {})"\
            .format(self.pid,   # not null field
                    "'{}'".format(self.worker_id) if self.worker_id is not None else 'NULL',
                    "'{}'".format(self.worker_type) if self.worker_type is not None else 'NULL',
                    self.resource_id if self.resource_id is not None else 'NULL',
                    level,  # not null field
                    "'{}'".format(task_id) if task_id is not None else 'NULL',
                    event,
                    "'{}'".format(message) if message is not None else 'NULL')

        cur.execute(query)
        self.conn.commit()

    def log_error(self, event, message, task_id=None):
        msg = self.print_console(event, message, task_id)
        self.commit_log(event, message, task_id, 0)
        raise RuntimeError(msg)

    def log_warning(self, event, message, task_id=None):
        self.print_console(event, message, task_id)
        self.commit_log(event, message, task_id, 1)

    def log_info(self, event, message, task_id=None):
        self.print_console(event, message, task_id)
        self.commit_log(event, message, task_id, 2)

    def log_debug(self, event, message, task_id=None):
        self.print_console(event, message, task_id)
        self.commit_log(event, message, task_id, 3)

    def print_console(self, event, message, task_id):
        msg = "worker id: {}, worker_type: {}, event: {}, message: {}, task_id: {}"\
            .format(self.worker_id, self.worker_type, event, message, task_id)
        print(msg)
        return msg
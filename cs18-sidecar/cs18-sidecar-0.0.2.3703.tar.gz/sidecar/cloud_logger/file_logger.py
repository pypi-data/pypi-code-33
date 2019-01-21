import os
from typing import List

from sidecar.const import Const
from . import ICloudLogger, LogEntry


class FileLogger(ICloudLogger):
    def __init__(self, app_names: List[str]):
        for app_name in app_names:
            app_folder = Const.get_app_folder(app_name)
            if not os.path.exists(app_folder):
                os.mkdir(app_folder)

    def write(self, log_entry: LogEntry):
        app_folder = Const.get_app_folder(log_entry.app)

        if not os.path.exists("/var/ftp/sandbox/logs"):
            os.makedirs("/var/ftp/sandbox/logs")

        filename = "/var/ftp/sandbox/logs/{0}.{1}-{2}.log".format(log_entry.instance.replace("docker://", ""),
                                                                  log_entry.app, log_entry.log_type)
        lines = ["[{LOG_TYPE}][{TIME}]{LINE}\n".format(LOG_TYPE=log_entry.log_type,
                                                       TIME=time.strftime('%Y-%m-%d %H:%M:%S'),
                                                       LINE=line) for time, line in log_entry.log_events]
        with open(filename, "at") as stream:
            stream.writelines(lines)


class FakeFileLogger(FileLogger):
    def __init__(self):
        super().__init__(app_names=[])

    def write(self, log_entry: LogEntry):
        pass

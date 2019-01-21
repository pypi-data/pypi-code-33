import time
from socket import gethostname
from getpass import getuser
import sys


class MLPCMetadata:
    def __init__(self):
        self.timestamp = ""  # Updated by bump_version()
        self.bump_timestamp()
        self.hostname = gethostname()
        self.username = getuser()
        self.python_platform = sys.platform
        self.python_version = sys.version
        self.mlpc_version = "0.0.16"

    def bump_timestamp(self):
        localtime = time.localtime()
        self.timestamp = time.strftime("%Y-%m-%d-%H%M%S", localtime)

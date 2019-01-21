import time
from socket import gethostname
from getpass import getuser
import sys
import os
import mlpc


METADATA_FILENAME = "mlpc_metadata.json"
MLPC_VERSION = "0.0.21"


class Metadata:
    def __init__(self):
        self.timestamp = ""  # Updated by update_timestamp()
        self.run_path = ""  # Updated by update_timestamp()
        self.hostname = gethostname()
        self.username = getuser()
        self.python_platform = sys.platform
        self.python_version = sys.version
        self.mlpc_version = MLPC_VERSION
        self.update_timestamp()

    def update_timestamp(self):
        localtime = time.localtime()
        self.timestamp = time.strftime("%Y-%m-%d-%H%M%S", localtime)
        self.run_path = os.path.join(mlpc.configuration.root_folder_path, self.timestamp)

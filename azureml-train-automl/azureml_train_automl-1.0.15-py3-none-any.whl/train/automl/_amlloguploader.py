# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for uploading aml log files."""
import os

from azureml._logging.debug_mode import debug_sdk
from azureml._history.utils.constants import (AZUREML_LOGS, AZUREML_LOG_FILE_NAME)

from azureml.core import Run
from .run import AutoMLRun


class _AMLLogUploader():
    def __init__(self, run, worker_id):
        self.run = run
        self.worker_id = str(worker_id)
        AZUREML_LOG_DIR = os.environ.get("AZUREML_LOGDIRECTORY_PATH", os.getcwd())
        self.azureml_log_file_path = os.path.join(AZUREML_LOG_DIR, AZUREML_LOG_FILE_NAME)

    def __enter__(self):
        debug_sdk()

    def __exit__(self, exc_type, exc_value, tb):
        has_azureml_log_file = os.path.exists(self.azureml_log_file_path)
        if has_azureml_log_file:
            self.run.upload_file(AZUREML_LOGS + "/" + AZUREML_LOG_FILE_NAME, self.azureml_log_file_path)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os
import time

LOG_FILE = os.path.abspath("azureml.log")
LOG_FORMAT = '%(asctime)s|%(name)s|%(levelname)s|%(message)s'
INTERESTING_NAMESPACES = [
    "azureml",
    "msrest.http_logger",
    "urllib2",
    "azure"
]

module_logger = logging.getLogger(__name__)


class diagnostic_log(object):
    def __init__(self, log_path=None, namespaces=None):
        self._namespaces = INTERESTING_NAMESPACES if namespaces is None else namespaces
        self._filename = LOG_FILE if log_path is None else log_path
        self._filename = os.path.abspath(self._filename)
        self._capturing = False

        formatter = logging.Formatter(LOG_FORMAT)
        formatter.converter = time.gmtime

        file_handler = logging.FileHandler(filename=self._filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self._handler = file_handler

    def start_capture(self):
        if self._capturing:
            module_logger.warning("Debug logs are already enabled at %s", self._filename)
            return

        print("Debug logs are being sent to {}".format(self._filename))

        for namespace in self._namespaces:
            module_logger.debug("Adding [%s] debug logs to this file", namespace)
            n_logger = logging.getLogger(namespace)
            n_logger.setLevel(logging.DEBUG)
            n_logger.addHandler(self._handler)
            # We do the below for strange environments like Revo + Jupyter
            # where root handlers appear to already be set.
            # We don't want to spew to those consoles with DEBUG emissions
            n_logger.propagate = 0

        self._capturing = True

    def stop_capture(self):
        if not self._capturing:
            module_logger.warning("Debug logs are already disabled.")
            return

        print("Disabling log capture. Resulting file is at {}".format(self._filename))

        for namespace in self._namespaces:
            module_logger.debug("Removing [%s] debug logs to this file", namespace)
            n_logger = logging.getLogger(namespace)
            n_logger.removeHandler(self._handler)

        self._capturing = False

    def __enter__(self):
        self.start_capture()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_capture()


_debugging_enabled = False


def debug_sdk():
    global _debugging_enabled
    if _debugging_enabled:
        module_logger.warning("Debug logs are already enabled at %s", LOG_FILE)
        return

    formatter = logging.Formatter(LOG_FORMAT)
    formatter.converter = time.gmtime

    file_handler = logging.FileHandler(filename=LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    module_logger.info("Debug logs are being sent to %s", LOG_FILE)

    for namespace in INTERESTING_NAMESPACES:
        module_logger.debug("Adding [%s] debug logs to this file", namespace)
        n_logger = logging.getLogger(namespace)
        n_logger.setLevel(logging.DEBUG)
        n_logger.addHandler(file_handler)
        # We do the below for strange environments like Revo + Jupyter
        # where root handlers appear to already be set.
        # We don't want to spew to those consoles with DEBUG emissions
        n_logger.propagate = 0

    _debugging_enabled = True

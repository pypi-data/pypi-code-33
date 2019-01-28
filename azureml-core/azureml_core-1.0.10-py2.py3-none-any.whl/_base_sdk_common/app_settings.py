# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import json
import logging

DEFAULT_FLIGHT = "default"
MASTER_FLIGHT = "master"

module_logger = logging.getLogger(__name__)


class AppSettings(object):
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "appsettings.json")
        try:
            with open(file_path, "r") as settings_file:
                self._settings = json.load(settings_file)
        except Exception as e:
            module_logger.debug("Failed to load flight from {} with exception: {}".format(file_path, e))
            self._settings = {"flight": DEFAULT_FLIGHT}

    def get_flight(self):
        return self._settings["flight"]

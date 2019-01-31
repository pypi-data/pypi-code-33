# -*- coding: utf-8 -*-

"""
Wrapper for a config dictionary. Lets the user safely request a value via a key,
with support for default values and for logging which keys were used and were missing.
"""

import json
import os

from k_util import pather
from k_util.logger import Logger

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Config:
    def __init__(self, data: dict=None):
        self.data = data if data is not None else {}
        self.keys_used = {}
        self.keys_miss = {}

    def get(self, key: str, default=None):
        """ """
        if key in self.data:
            self.keys_used[key] = self.data[key]
            return self.data[key]
        else:
            self.keys_miss[key] = default
            return default

    def __call__(self, key: str, default=None):
        """ Alias for the get method. """
        return self.get(key, default)

    def __getitem__(self, key: str):
        self.keys_used[key] = self.data[key]
        return self.data[key]

    def __str__(self):
        return f"[Config Wrapper: {str(self.data)}]"

    # ===================================================================================================
    # Generate Summary
    # ===================================================================================================

    def generate_config_summary(self, output_dir: str):
        """ Print the hit/miss results from loading the config. """
        self._show_config_value_list("Config Values Loaded", self.keys_used)
        self._show_config_value_list("Config Values Missing", self.keys_miss)

        # Also write the results to the artifact folder.
        config_path = os.path.join(output_dir, "config_summary.json")
        data = {
            "config_loaded": self.keys_used,
            "config_missing": self.keys_miss
        }
        pather.create(config_path)
        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def _show_config_value_list(title: str, config_map: dict):
        """ Show in console the keys used and the keys missing from the config. """
        Logger.header(title)
        if len(config_map) == 0:
            Logger.indent()
            Logger.log("None")
        else:
            for k, v in config_map.items():
                Logger.field(k, v)

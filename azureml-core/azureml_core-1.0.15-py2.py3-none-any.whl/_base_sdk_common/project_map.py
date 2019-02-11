# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os.path import expanduser, join, dirname
import json
import os


class ProjectMap(object):
    def __init__(self, file_path=join(expanduser("~"), ".azureml", ".projectMap")):
        dir_name = dirname(file_path)
        try:
            os.mkdir(os.path.abspath(dir_name))
        except OSError:
            # Ignoring exception if the directory already exists.
            pass
        self.file_path = file_path

    def lookup_project(self, project_id):
        cache = self._load_cache()
        if project_id in cache:
            return cache[project_id]
        return None

    def save_project(self, project_id, scope):
        cache = self._load_cache()
        cache[project_id] = scope
        self._save_cache(cache)

    def _load_cache(self):
        if not os.path.exists(os.path.abspath(self.file_path)):
            return {}
        with open(self.file_path, "r") as file:
            return json.load(file)

    def _save_cache(self, cache):
        with open(self.file_path, "w+") as file:
            json.dump(cache, file)

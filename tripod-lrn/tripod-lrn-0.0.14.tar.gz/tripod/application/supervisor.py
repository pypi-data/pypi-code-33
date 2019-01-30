# -*- coding: utf-8 -*-
"""
module supervisor.py
--------------------------------
    defines a simple and generic application application class used to run the application under a
    supervisor management.
"""
from supervisor import supervisord
import os


class SupervisordApp(object):
    """
    Supervisord application.
    """

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        config_path = self.config.get("supervisor.config_path", None)
        config_path = os.path.expanduser(config_path)
        if config_path is not None and os.path.exists(config_path):
            args = ["-c", config_path, "-n"]
            # args = {"-c": config_path, "-n":"true"}
        else:
            raise RuntimeError("Could not find supervisord.conf file.")
        supervisord.main(args)

# -*- coding: utf-8 -*-
"""
Module events.py
-----------------------
A class that represents the tripod application events that are called during the application life cycle.
"""
from .app_event import AppEvent
from tripod import utils


class AppHooks(object):
    """Represents the Tripod application hook functions.
    A class that represents the tripod application hook functions
    that are called during the application life cycle.
    """
    def __init__(self, module_path=""):
        """
        App events initialization.
        :param module_path: module doted path.
        """
        # application events
        if module_path != "":
            module_path = module_path
        self.before_app_init = AppEvent("{}.before_app_init".format(module_path))
        self.on_app_init = AppEvent("{}.on_app_init".format(module_path))
        self.after_app_init = AppEvent("{}.after_app_init".format(module_path))
        self.on_app_exit = AppEvent("{}.on_app_exit".format(module_path))
        self.load_hooks_from_file(module_path)

    def load_hooks_from_file(self, prefix=""):
        mod_str = "tripod_hooks"
        if prefix != "":
            mod_str = "{}.{}".format(prefix, mod_str)

        if utils.check_module_existence(mod_str):
            app_hooks = utils.import_string(mod_str)

            # register the before app initialization hook
            if hasattr(app_hooks, "before_app_init"):
                before_func = getattr(app_hooks, "before_app_init")
                self.before_app_init += before_func

            # register the on app initialization hook
            if hasattr(app_hooks, "on_app_init"):
                on_func = getattr(app_hooks, "on_app_init")
                self.on_app_init += on_func

            # register the before app initialization hook
            if hasattr(app_hooks, "after_app_init"):
                after_func = getattr(app_hooks, "after_app_init")
                self.after_app_init += after_func

            # register the on app initialization hook
            if hasattr(app_hooks, "on_app_exit"):
                after_func = getattr(app_hooks, "on_app_exit")
                self.on_app_exit += after_func
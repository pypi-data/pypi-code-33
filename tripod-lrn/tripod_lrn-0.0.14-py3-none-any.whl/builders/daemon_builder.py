# -*- coding: utf-8 -*-
"""
module daemon_loaders.py
---------------------------
Defines loader functions to daemon applications.
"""
from tripod.application.supervisor import SupervisordApp
from tripod.events.app_hooks import AppHooks
from tripod.application.daemon import DaemonApplication
from .. import utils


def build_daemon_app(config, instance):
    """
    Daemon app builder function.
    :return: Daemon application.
    """
    app_hooks = AppHooks()
    # runs the before app initialization hook
    app_hooks.before_app_init.send(None)
    app = DaemonApplication(app_hooks, config)
    instance.app = app

    if utils.check_module_existence("main"):
        main_mod = utils.import_module("main")
        main_func = getattr(main_mod, "main")
        app.main = main_func
    else:
        raise EnvironmentError("Could not find the main application module.")
    return app


def build_app(dev, single, instance):
    """
    Tripod Daemon Application function builder.
    :param dev: if true it will build the app in development mode.
    :param single: if true builds a single instance application.
    :param instance: the program instance that is calling this function.
    """
    # os system vars
    if dev or single:  # runs app in development mode
        app = build_daemon_app(instance.app_config, instance)
    else:
        app = SupervisordApp(instance.app_config)
    return app

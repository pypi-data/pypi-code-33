# -*- coding: utf-8 -*-
"""
Module settings.py
----------------------
Is a project configuration file.
All variables defined on this file will loaded by the application.

When needed all configurations defined on this file can be recovered from the application config object
(.i.e. `tripod.current_app.config`).
"""
import os

DEBUG = False
TESTING = False
PROPAGATE_EXCEPTIONS = True

# logger path configuration
LOG_GROUP = "/"

# os system vars
tripod_config = os.getenv('TRIPOD_APP_CONFIG', False)
stream_logs_disable = os.getenv('STREAM_LOGS_DISABLE', False)

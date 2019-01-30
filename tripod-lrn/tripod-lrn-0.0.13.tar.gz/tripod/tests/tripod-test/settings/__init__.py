# -*- coding: utf-8 -*-
"""
Module settings:
-------------------
 | Provides the project configuration files.
 | The base settings are found on the module *root* path. i.e. in in :file:`settings.py`.
 | The base `settings` file can be overridden and specialized per environment type.
 | The *environment type* is defined by setting the **TRIPOD_APP_CONFIG** *system variable*. 
 | Possible environmnet types:
 |   1. development (**default**)
 |   2. production
 |   3. test
    
 |   If no environment is set, then the **default** is used while running the application.
    
 |   Each environment specific settings are found on it respective submodules that are named accordingly 
    (i.e. `development`, `production`, `test`).
"""
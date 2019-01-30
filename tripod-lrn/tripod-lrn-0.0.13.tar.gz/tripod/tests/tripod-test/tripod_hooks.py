# -*- coding: utf-8 -*-
"""
module tripod_hooks.py
----------------------
Provides access to application lifecycle hook functions that are called 
during the application life-cycle.
"""

def before_app_init(sender):
    """Callback before app initialization.
    Called before initializing the flask app object.
    """
    # suppress warnings from numpy compilation
    print("before_app_init")


def on_app_init(app):
    """On app initialization hook. 
    Called after app initialization and before running the app.
    :param app: `falsk.Flask` app object.
    """
    print('Init app.')
# -*- coding: utf-8 -*-
"""
Tripod is the evolution of our old-project quick-starter flask-manager.

Tripod provides command-line utilities for a set of common projects/applications lifecycle management.
It is intended to give support for common administrative, development and deployment tasks.

Additionally it provides project templates initialization.

This pack is intended to be flexible enough to give users a easy ways to extend the commands and their behaviours.

Task from this module are called from the command line in the following format:
`tripod [command]`
"""
from .local import LocalProxy


def __get_app__():
    from .main import app
    return app


app = LocalProxy(__get_app__)


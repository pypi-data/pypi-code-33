#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Global configuration options expressed in environment variables."""
from os import getenv
from os.path import expanduser, join

CONFIG_FILE = getenv('UNIQUEID_CONFIG', join(
    expanduser('~'), '.pacifica-uniqueid', 'config.ini'))
CHERRYPY_CONFIG = getenv('UNIQUEID_CPCONFIG', join(
    expanduser('~'), '.pacifica-uniqueid', 'cpconfig.ini'))

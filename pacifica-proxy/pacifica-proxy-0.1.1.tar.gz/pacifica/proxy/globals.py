#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Global configuration options expressed in environment variables."""
from os import getenv
from os.path import expanduser, join

CONFIG_FILE = getenv('PROXY_CONFIG', join(
    expanduser('~'), '.pacifica-proxy', 'config.ini'))
CHERRYPY_CONFIG = getenv('PROXY_CPCONFIG', join(
    expanduser('~'), '.pacifica-proxy', 'cpconfig.ini'))

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Configuration reading and validation module."""
from os import getenv
try:
    from ConfigParser import SafeConfigParser
except ImportError:  # pragma: no cover python 2 vs 3 issue
    from configparser import ConfigParser as SafeConfigParser
from .globals import CONFIG_FILE


def get_config():
    """Return the ConfigParser object with defaults set."""
    configparser = SafeConfigParser()
    configparser.add_section('archiveinterface')
    configparser.set('archiveinterface', 'url', getenv(
        'ARCHIVEINTERFACE_URL', 'http://127.0.0.1:8080'))
    configparser.add_section('metadata')
    configparser.set('metadata', 'url', getenv(
        'METADATA_URL', 'http://127.0.0.1:8121'))
    configparser.set('metadata', 'status_wait', getenv(
        'METADATA_STATUS_WAIT', '5'))
    configparser.set('metadata', 'status_attempts', getenv(
        'METADATA_STATUS_ATTEMPTS', '40'))
    configparser.set('metadata', 'status_url', getenv(
        'METADATA_STATUS_URL', 'http://127.0.0.1:8121/keys'))
    configparser.add_section('nginx')
    configparser.set('nginx', 'accel', getenv(
        'NGINX_ACCEL', 'False'))
    configparser.read(CONFIG_FILE)
    return configparser

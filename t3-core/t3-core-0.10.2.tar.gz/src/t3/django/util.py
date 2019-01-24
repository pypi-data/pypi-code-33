import sys
from os import environ
from os.path import dirname, abspath
from functools import lru_cache


@lru_cache()
def get_base_dir():
    """
    Use DJANGO_SETTINGS_MODULE to determine where the root project lives.

    This is used by Django's core code & is set in both manage.py & wsgi.py

    The assumption is that the path is `src.{project}.settings`
    """
    _settings_module = environ['DJANGO_SETTINGS_MODULE']
    _settings_file = sys.modules[_settings_module].__file__

    return dirname(dirname(dirname(abspath(_settings_file))))

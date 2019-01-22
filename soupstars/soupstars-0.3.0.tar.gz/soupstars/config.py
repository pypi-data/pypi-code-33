"""
Configuration
-------------

Configuration objects work like a dictionary, with values determined by
environment variables.

>>> import os
>>> from soupstars.config import SoupstarsConfig
>>> config = SoupstarsConfig()
"""

import os
import importlib


class SoupstarsConfig(object):
    """
    Determines the configuration values:

    :var SOUPSTARS_HOME: The directory used to store parsers and caches.
        Defaults to `~/.soupstars`.
    :var PARSERS_PATH: The directory searched for additional parsers. Defaults
        to `~/.soupstars/parsers`.
    :var LOAD_EXAMPLES: Whether to include the example parsers installed with
        soupstars when running the flask server.
    :var FILESYSTEM_CACHE_PATH: The directory used for storing cached objects
        by `FilesystemCache`. Defaults to `~/.soupstars/cache`.
    """

    def __init__(self):
        self.SOUPSTARS_HOME = self._set_soupstars_home()
        self.SOUPSTARS_CACHE_PATH = self._set_cache_path()
        self.SOUPSTARS_LOAD_EXAMPLES = self._set_load_examples()
        self.SOUPSTARS_EXAMPLES_PATH = self._set_soupstars_example_path()
        self._set_directories()

    def _set_soupstars_home(self):
        home = os.environ.get('SOUPSTARS_HOME') \
               or os.path.join(os.path.expanduser('~'), 'soupstars')
        return home

    def _set_load_examples(self):
        if os.environ.get("SOUPSTARS_LOAD_EXAMPLES") in ('False', 0):
            return False
        else:
            return True

    def _set_soupstars_example_path(self):
        _soupstars_path = os.path.abspath(os.path.dirname(__file__))
        SOUPSTARS_EXAMPLES_PATH = os.path.join(_soupstars_path, "examples")
        return SOUPSTARS_EXAMPLES_PATH

    def _set_cache_path(self):
        return os.path.join(self.SOUPSTARS_HOME, 'cache')

    def _set_directories(self):
        for path in [self.SOUPSTARS_HOME, self.SOUPSTARS_CACHE_PATH]:

            try:
                os.mkdir(path)
            except FileExistsError:
                pass

import os
import json

import appdirs
from configparser import ConfigParser

from scotty.core.exceptions import ScottyException


def load_settings():
    global settings
    config_file = ConfigFile()
    path = config_file.path
    config_parser = ConfigParser()
    config_parser.read(path)
    settings = ScottyConfig(config_parser, config_file.base_dir)
    return settings


def get(section, option, abspath=False):
    if 'settings' not in globals():
        load_settings()
    setting_value = settings.get(section, option, abspath)
    return setting_value


class ConfigFile(object):
    _config_suffixes = ['.conf']

    def __init__(self):
        self._appdirs = appdirs.AppDirs('scotty', multipath='/etc')
        self._path = None
        self._base_dir = None

    @property
    def _config_files(self):
        config_files = []
        for path in self._config_search_paths:
            for suffix in self._config_suffixes:
                config_file = os.path.join(path, 'scotty{}'.format(suffix))
                config_files.append(config_file)
        return config_files

    @property
    def _config_search_paths(self):
        search_paths = []
        search_paths.append(self._unix_home_config)
        search_paths.append(self._home_etc)
        search_paths.append(self._unix_home_etc)
        search_paths.append(self._site_etc)
        search_paths.append(self._unix_site_etc)
        search_paths.append(self._app_config)
        return search_paths

    @property
    def _app_config(self):
        here = os.path.abspath(os.path.dirname(__file__))
        here = os.path.join(here, '../../')
        here = os.path.normpath(here)
        return os.path.join(here, 'etc')

    @property
    def _unix_home_config(self):
        return os.path.join(os.path.expanduser(os.path.join('~', '.config')), 'scotty')

    @property
    def _home_etc(self):
        return os.path.join(os.path.expanduser(os.path.join('~', '.local/etc')), 'scotty')

    @property
    def _unix_home_etc(self):
        return '/usr/local/etc/scotty'

    @property
    def _site_etc(self):
        return self._appdirs.site_config_dir

    @property
    def _unix_site_etc(self):
        return '/etc/scotty'

    def _find_config_file(self):
        for path in self._config_files:
            if os.path.exists(path):
                return path
        return None

    @property
    def path(self):
        if not self._path:
            self._path = self._find_config_file()
        return self._path

    @property
    def base_dir(self):
        if not self._base_dir:
            self._base_dir = os.path.dirname(self._path)
        return self._base_dir


class ScottyConfig(object):
    _config_type = {
        'logging': {'log_format': 'raw'},
        'resultstores': {'stores': 'json'},
        'owncloud': {
            'enable': 'boolean',
            'params': 'json'
        },
    }

    def __init__(self, config_parser, base_dir):
        self._config_parser = config_parser
        self._base_dir = base_dir

    def get(self, section, option, abspath=False):
        type_ = self._type(section, option)
        parse_method_name = '_parse_{}'.format(type_)
        parse_method = getattr(self, parse_method_name)
        value = parse_method(section, option)
        if abspath:
            value = self._abspath(value)
        return value

    def _abspath(self, path):
        if not os.path.isabs(path):
            path = os.path.join(self._base_dir, path)
            path = os.path.normpath(path)
        return path

    def _parse_raw(self, section, option):
        value = self._config_parser.get(section, option, raw=True)
        return value

    def _parse_None(self, section, option):
        value = self._config_parser.get(section, option)
        return value

    def _parse_json(self, section, option):
        value = self._config_parser.get(section, option)
        value = json.loads(value)
        return value

    def _parse_boolean(self, section, option):
        value = self._config_parser.getboolean(section, option)
        return value

    def _type(self, section, option):
        type_ = None
        if section in self._config_type:
            type_ = self._config_type[section].get(option, None)
        return type_

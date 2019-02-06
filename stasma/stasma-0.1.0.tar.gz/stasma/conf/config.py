import json
import logging
import os
import warnings
from configparser import ConfigParser
from logging import config as log_conf
from os.path import dirname


def level_up(path, n=0):
    for i in range(n):
        path = dirname(path)
    return path


config_parser = ConfigParser()

env_variable_config = os.environ.get('STASMA_CONFIG', '')
venv_config = os.path.join(os.environ.get('VIRTUAL_ENV', ''), 'conf', 'stasma_conf.ini')
default_config = os.path.join(os.path.dirname(__file__), "stasma_conf.ini")

# read configuration file
if os.path.isfile(env_variable_config):
    config_file = env_variable_config
elif os.path.isfile(venv_config):
    config_file = venv_config
elif os.path.isfile(default_config):
    config_file = default_config
else:
    warnings.warn("Couldn't resolve configuration file. To define it \n "
                  "  - Set the environment variable STASMA_CONFIG, or \n "
                  "  - Add conf/stasma_conf.ini under your virtualenv root \n ", Warning)

CONFIG_FILE = config_file
LOG_CONFIG = os.path.join(dirname(__file__), 'logging.json')


def set_up_logging():
    if os.path.isfile(LOG_CONFIG):
        with open(LOG_CONFIG) as f:
            conf_dict = json.loads(f.read())
        log_conf.dictConfig(conf_dict)
    else:
        logging.basicConfig(level=logging.INFO)


def read_and_update_config(conf_path=None):
    if not conf_path:
        conf_path = CONFIG_FILE

    if not os.path.isfile(conf_path):
        msg = (
            "Couldn't find configuration file. Using default settings.\n"
            "   To customize configuration using file either\n"
            "    - specify config with environment variable STASMA_CONFIG\n"
            "  -   add conf/elisa_conf.ini under your virtualenv root \n")
        warnings.warn(msg, Warning)
        return

    config_parser.read(conf_path)
    update_config()


def update_config():
    if config_parser.has_section('general'):
        global LOG_CONFIG
        LOG_CONFIG = config_parser.get('general', 'log_config') \
            if config_parser.get('general', 'log_config') else LOG_CONFIG


read_and_update_config()

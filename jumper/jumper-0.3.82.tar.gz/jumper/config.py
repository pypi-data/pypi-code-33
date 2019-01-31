import os
import json
from .common import MissingFileError

config_file_name = 'config.json'
if 'JUMPER_STAGING' in os.environ:
    config_file_name = 'config.staging.json'
if 'JUMPER_STAGING_INBAR' in os.environ:
    config_file_name = 'config.inbar.json'
JUMPER_DIR = os.path.join(os.path.expanduser('~'), '.jumper')
DEFAULT_CONFIG = os.path.join(JUMPER_DIR, config_file_name)


def load_config(config_file=None):
    config_file = config_file or DEFAULT_CONFIG
    if not os.path.isfile(config_file):
        raise MissingFileError("File not found: {}".format(config_file))
    with open(config_file) as config_data:
        return json.load(config_data)


def get_token(config_file=None):
    config = load_config(config_file)
    if 'token' in config:
        return config['token']
    else:
        raise ValueError("token is missing in: {}".format(config_file))


def set_token(token, config_file=None):
    config_file = config_file or DEFAULT_CONFIG
    config = dict()
    try:
        config = load_config(config_file)
    except MissingFileError:
        pass

    config['token'] = token

    dirname = os.path.dirname(config_file)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    with open(config_file, 'w') as file:
        file.write(json.dumps(config))

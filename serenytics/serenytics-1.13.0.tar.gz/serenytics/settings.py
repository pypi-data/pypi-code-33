import base64
import json
import logging
from logging.config import dictConfig
import os


def load_environment_variable(key, default=None):
    """
    Retrieves env vars and makes Python boolean replacements
    """
    val = os.getenv(key, default)
    if isinstance(val, str) and val.lower() == 'true':
        return True
    elif isinstance(val, str) and val.lower() == 'false':
        return False
    return val


SERENYTICS_API_DOMAIN = load_environment_variable('PYTHON_CLIENT_API_DOMAIN', 'https://api.serenytics.com')


def enable_log(log_level=logging.INFO):
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(asctime)s [%(levelname)s] %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'loggers': {
            'requests.packages.urllib3': {
                'level': logging.WARNING
            },
            'paramiko': {
                'level': logging.WARNING
            },
        },
        'root': {
            'handlers': ['console'],
            'level': log_level,
        },
    }
    dictConfig(config)


def __get_script_params():
    """
    :return: dict containing params passed to the script
    """
    try:
        # try to load params from json file
        with open('params.json') as params_file:
            params = json.load(params_file)
        return params
    except IOError:
        # if no file exists, try to load params from environment (convenient for tests)
        base64_json_params = os.environ.get('_SERENYTICS_PARAMS')
        if base64_json_params:
            try:
                params = json.loads(base64.b64decode(base64_json_params).decode('utf-8'))
                return params
            except:
                logging.warning('Failed to load params from environment variable "_SERENYTICS_PARAMS"')
                return {}


script_params = __get_script_params()

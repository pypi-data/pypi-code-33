import os
import re
from typing import Any, Dict

__author__ = 'Peter Magnusson'
__license__ = 'MIT'
__copyright__ = 'Copyright 2019 Peter Magnusson'

reTrue = re.compile(r'^(yes|on|true|enabled)$', re.IGNORECASE)
reFalse = re.compile(r'^(no|off|false|disabled)$',  re.IGNORECASE)


def options() -> dict:
    """Get options from environment variables
    Any env.variable prefixed with DEBUG_ will be included
    """
    # for key in os.environ.keys():
    keys = [key for key in os.environ.keys()
            if key.lower().startswith('debug_')]
    obj = {}  # type: Dict[str, Any]
    for key in keys:
        prop = key[6:].lower()
        val = os.environ.get(key, '')  # type: str
        if reTrue.match(val):
            obj[prop] = True
        elif reFalse.match(val):
            obj[prop] = False
        elif val == 'null':
            obj[prop] = None
        else:
            obj[prop] = int(val, 10)

    return obj


def load():
    return os.environ.get('DEBUG', '')


def save(namespaces):
    os.environ['DEBUG'] = namespaces

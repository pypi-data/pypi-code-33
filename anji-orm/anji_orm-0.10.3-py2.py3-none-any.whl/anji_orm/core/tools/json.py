from datetime import datetime
from typing import Dict

try:
    import usjon as json
except ImportError:
    import json  # type: ignore


__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["json_dumps", "json_loads"]

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
DATETIME_DICT_FIELD = "$data"


def _json_default(value):
    if isinstance(value, datetime):
        return {DATETIME_DICT_FIELD: value.strftime(DATETIME_FORMAT)}
    return value


def _json_object_hook(value):
    if isinstance(value, dict) and len(value) == 1 and DATETIME_DICT_FIELD in value:
        return datetime.strptime(value[DATETIME_DICT_FIELD], DATETIME_FORMAT)
    return value


def json_dumps(obj: Dict) -> str:
    return json.dumps(obj, default=_json_default)


def json_loads(raw_json: str) -> Dict:
    return json.loads(raw_json, object_hook=_json_object_hook)

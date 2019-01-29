import datetime
import decimal
import inspect
import json
import re
import os
import sys
from itertools import islice
from typing import Iterable
import types
import logging

from ..define.const import USE_TORNADO

tornado_available = False
HTTPServer = None
PeriodicCallback = None
IOLoop = None

if USE_TORNADO:
    tornado_available = True
    try:
        # noinspection PyPackageRequirements
        from tornado.ioloop import IOLoop, PeriodicCallback
        # noinspection PyPackageRequirements
        from tornado.httpserver import HTTPServer
    except ImportError:
        tornado_available = False


async_decorator = types
if tornado_available:
    try:
        # noinspection PyPackageRequirements
        from tornado import gen as async_decorator
    except ImportError:
        pass

try:
    from psycopg2 import ProgrammingError as PostgreSQLError
except ImportError:
    class PostgreSQLError(BaseException):
        pass


def is_iter_but_str(item):
    return not isinstance(item, str) and isinstance(item, Iterable)


def to_iter(item):
    if is_iter_but_str(item):
        return item
    else:
        return item,


def _json_encoder(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S.%f%z')
    if isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')
    if isinstance(obj, datetime.time):
        return obj.strftime('%H:%M:%S.%f%z')
    if isinstance(obj, datetime.timedelta):
        return obj.total_seconds()
    if isinstance(obj, bytes):
        try:
            return obj.decode('UTF8')
        except Exception:
            return str(obj)
    return repr(obj)


def json_dumps_with_dt(data, indent=0):
    return json.dumps(data, default=_json_encoder, indent=indent)


def get_project_path():
    return os.path.abspath(os.path.dirname(sys.argv[0]))


relative_path = __file__.replace(get_project_path(), '')
# app_path = os.path.normpath(os.path.split(relative_path)[0]).split(os.sep)[1]
project_path_pattern = re.compile(
    r'^{}/'.format(
        get_project_path(),
        # app_path
    )
)


def compose_own_call_stack(
        skip_methods,
        skip_paths,
        result_length=1,
        look_up_stop_idx=27,
        from_index=0,
        name_dummy='<unknown>',
        frame_list=None,
):
    outer_frames = frame_list if frame_list is not None else inspect.stack()

    def is_project_outer_frame(item):
        try:
            file_name = item.f_code.co_filename
            return (
                project_path_pattern.match(file_name)
                and
                "site-packages" not in file_name
                and
                "lib/python" not in file_name
            )
        except (IndexError, AttributeError):
            return False

    def compose_frame_path_object(item):
        try:
            file_name = project_path_pattern.sub(
                '',
                item.f_code.co_filename,
                1,
            )
            method_name = item.f_code.co_name
        except (IndexError, AttributeError):
            return None
        if method_name in skip_methods:
            return None
        if skip_paths in file_name:
            return None
        return {
            'full_path': file_name + ':' + method_name,
            'short_path': method_name,
        }

    lookup_list = [
        el
        for el in outer_frames[from_index:look_up_stop_idx]
        if is_project_outer_frame(el)
    ]
    composed_data_list = [
        compose_frame_path_object(el)
        for el in lookup_list
    ]
    compacted_list = [
        el
        for el in composed_data_list
        if el is not None
    ]
    result_dicts = list(islice(compacted_list, result_length))

    return result_dicts


def dict_from_json(data):
    """
    Return dict from json-string or dict
    :param data: string or dict
    :return: dict
    """
    try:
        data_dict = json.loads(data)
    except ValueError as e:
        logging.warning('JSON parse error: %s Data: %s.', e, data)
        data_dict = data
    return data_dict

import functools
import logging
import os
import sys
import time

import threading
from threading import _DummyThread
from python_agent import bootstrap

log = logging.getLogger(__name__)


def retries(logger, tries=3, quiet=True):
    def inner(f):
        @functools.wraps(f)
        def inner_args(*args, **kwargs):
            for i in range(tries):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    logger.warn("failed try #%s running function %s. args: %s exception: %s"
                                % (str(i + 1), f.__name__, str(args), str(e)), exc_info=True)
                    time.sleep(2 * i)
            if quiet:
                return
            raise

        return inner_args

    return inner


def exception_handler(log, quiet=True, message=None):
    def f_exception_handler(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.exception("%s. Error: %s. Args: %s. Kwargs: %s" % (message, str(e), args, kwargs))
                if not quiet:
                    raise

        return wrapper

    return f_exception_handler


def get_top_relative_path(filepath, workspacepath=None):
    start = workspacepath or os.getcwd()
    start = os.path.abspath(start)
    return os.path.relpath(filepath, start)


def get_python_path():
    python_path = os.environ.get("PYTHONPATH")
    if python_path:
        python_paths = python_path.split(os.pathsep)
        # we're filtering out the agent's boostrap path in case we're running with the run command
        # the agent injects a python path we want to ignore
        bootstrap_path = bootstrap.__name__.replace(".", os.sep)
        python_paths = [path for path in python_paths if bootstrap_path not in path]
        python_path = python_paths[0] if python_paths else None
    return python_path


def to_str_obj(obj):
    return '\n'.join("%s=%s" % (key, value) for key, value in obj.__dict__.items())


def to_str_obj_one_line(obj):
    line_format = "(%s)"
    arg_format = "%s=%s"
    return line_format % (','.join(arg_format % (key, value) for key, value in obj.__dict__.items()))


def to_str_list(title, obj_list):
    """
    Creates a string representation of a given list  as a title and zero-based numbered entries:
    <title> :
    [0] <entry>
    ...
    [n=len-1] <entry>

    If a list entry has implemented method __str__ , it is called.
    Otherwise the default object reference is printed

    :param title:
    :param obj_list:
    :return:
    """
    ctr = 0
    to_str = title

    if len(obj_list) == 0:
        to_str += ': empty'
    else:
        line_format = '\t[%d]:\t%s'
        to_str += ':\n' + '\n'.join(line_format % (index, e) for index, e in enumerate(obj_list))

    return to_str


def to_str_dict(title, obj_dict):
    """
    Creates a string representation of a given dictionary as a title and zero-based numbered entries:
    <title> :
    [0] <key> -> <value>
    ...
    [n=len-1] <key> -> <value>

    If a dictionary key/value has implemented method __str__ , it is called.
    Otherwise the default object reference is printed

    :param title:
    :param obj_dict:
    :return:
    """
    ctr = 0
    to_str = title

    if len(obj_dict) == 0:
        to_str += ': empty'
    else:
        line_format = '\t[%d]:\t%s->%s'
        to_str += ':\n' + '\n'.join(line_format % (index, key, obj_dict[key]) for index, key in enumerate(obj_dict.keys()))

    return to_str


def trace(f, trace_function):
    @functools.wraps(f)
    def inner_trace(*args, **kwargs):
        value = f(*args, **kwargs)
        if type(value) == _DummyThread:
            sys.settrace(trace_function)
            threading.settrace(trace_function)
        return value
    return inner_trace

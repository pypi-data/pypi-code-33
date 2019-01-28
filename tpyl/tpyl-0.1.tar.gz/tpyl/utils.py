import imp
import os
import sys

from six import string_types
from six.moves import urllib


def is_string(obj):
    """
    Returns True if @obj is a string, False otherwise.
    """
    return isinstance(obj, string_types)


def is_list(obj):
    """
    Check if @obj is instance of list or tuple.
    """
    return isinstance(obj, (list, tuple,))


def to_list(obj, class_type=list):
    """
    Returns the @obj if is a list. Returns a tuple with the @obj otherwise.
    """
    return class_type(obj if is_list(obj) else (obj,))


def to_tuple(obj):
    """
    Returns the @obj if is a tuple. Returns a tuple with the @obj otherwise.
    """
    return to_list(obj, class_type=tuple)


def is_executable(path):
    """
    Returns True if the file @path is executable, False otherwise.
    """
    return os.access(path, os.X_OK)


def is_url(url):
    """
    Returns True if the @url is a valid url, False otherwise.
    """
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme and parsed.netloc


def import_module(file_path='', sep=os.path.sep, pyclean=True):
    """
    Imports a module from a gitven @file_path.
    """
    path, ext = os.path.splitext(file_path)
    package = os.path.basename(path).replace(sep, '.')
    dirname = os.path.dirname(file_path)

    if dirname not in sys.path:
        sys.path.insert(0, dirname)

    try:
        module = import_non_local(package, paths=dirname)
        return module
    finally:
        sys.path.remove(dirname)
        if pyclean:
            pyc_path = os.path.join(dirname, '%s.pyc' % package)
            if os.path.exists(pyc_path):
                os.remove(pyc_path)


def import_non_local(name, custom_name=None, paths=None):
    """
    Returns the module named as @name. If @custom_name is provided the module
    will be named as @custom_name internally.
    """
    paths = [path for path in to_tuple(paths or '') if path]
    custom_name = custom_name or name

    f, pathname, desc = imp.find_module(name, paths or sys.path[1:])
    module = imp.load_module(custom_name, f, pathname, desc)
    if f:
        f.close()

    return module

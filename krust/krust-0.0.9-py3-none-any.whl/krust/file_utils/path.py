# -*- coding:utf-8 -*-

import six
import os
import sys
import re
import warnings


__all__ = [
    'P',
    'PWD', 'DIRNAME', 'BASENAME', 'ensure_slash', 'add_slash',
    'CD',
    'get_rel_path', 'add_path_delta', 'find_link_orig',
    'get_ext', 'strip_ext', 'sub_ext',
    'is_glob', 'is_hidden', 'is_file', 'is_dir', 'is_link',
]


# status: done
def P(path):
    """expand ~ and $ in the path"""
    if path is None:
        return None
    else:
        return os.path.expanduser(os.path.expandvars(path))


# status: done
def PWD():
    """Get current dir, as pwd in shell"""
    return os.getcwdu()


# status: usable
def DIRNAME(fname=None, absolute=False):
    if fname is None:
        fname = sys.modules['__main__'].__dict__['__file__']
        return os.path.dirname(os.path.abspath(fname))
    else:
        if absolute:
            fname = os.path.abspath(fname)
        return os.path.dirname(fname)


# status: done
BASENAME = os.path.basename


# status: done
def ensure_slash(path):
    """Add a slash to the end of path if not exist."""
    return path.rstrip('/') + '/'


# status: deprecated
def add_slash(path):
    warnings.warn("Deprecated, use ensure_slash(path) instead.", DeprecationWarning)


# status: done
def CD(path=None):
    """CD changes dir
    """
    if path is None:
        path = P('~')
    else:
        path = P(path)
    if path == '':  # For certain reason, only None is treated as "go to home folder", while "" is treated as no-op.
        return
    return os.chdir(path)


# status: done
def get_rel_path(path, base):
    """get relative path, e.g., get_rel_path('abc/de/fg', 'abc') => 'de/fg'
    """
    lb = len(base)
    assert path[:lb] == base
    if len(path) == lb:
        rel_path = ''
    elif path[lb] == '/':
        rel_path = path[lb+1:]
    else:
        rel_path = path[lb:]
    return rel_path


def add_path_delta(path, delta):
    """
    Add delta to pathrent path, with some cleaning by the way.
    :param path: pathrent path
    :param delta: delta
    :return: new path or raises ValueError

    >>> add_path_delta('/a/b/c', 'd/e')
    '/a/b/c/d/e'
    >>> add_path_delta('a/b/c', 'd/e')
    'a/b/c/d/e'
    >>> add_path_delta('a/b/c', '/d/e')
    '/d/e'
    >>> add_path_delta('/a/b/c', '../d/./e')
    '/a/b/d/e'
    >>> add_path_delta('/a/..//c', 'd/e')
    '/c/d/e'
    >>> add_path_delta('////', '')
    '/'
    >>> add_path_delta('a/b', '../..')
    ''
    >>> add_path_delta('/a/b', '../../..')
    Traceback (most recent call last):
        ...
    ValueError: Path delta out of bound: /a/b + ../../..
    """
    if delta.startswith('/'):
        absolute = True
        steps = delta[1:].split('/')
    else:
        absolute = path.startswith('/')
        steps = path.split('/') + delta.split('/')

    parts = []
    for step in steps:
        if step in ('.', ''):
            continue
        elif step == '..':
            try:
                parts.pop()
            except IndexError:
                raise ValueError(u"Path delta out of bound: {} + {}".format(path, delta))
        else:
            parts.append(step)

    res_path = '/'.join(parts)
    if absolute:
        res_path = '/' + res_path

    return res_path


# status: done
def find_link_orig(path, max_depth=99):
    """Try to find the orig of a link."""
    count = 0
    while count < max_depth:
        if os.path.islink(path):
            path = os.readlink(path)
        else:
            return path
        count += 1
    return path


# status: done
def get_ext(path):
    """get .ext from a path"""
    return os.path.splitext(path)[1]


# status: done
def strip_ext(path):
    """strips .ext from a path"""
    return os.path.splitext(path)[0]


# status: done
def sub_ext(orig, new_ext):
    """sub .ext with a new one"""
    if not new_ext.startswith('.'):
        new_ext = '.' + new_ext
    return strip_ext(orig) + new_ext


# status: done
def is_glob(path):
    if not isinstance(path, six.string_types):
        return False

    return '*' in path or '?' in path or re.match(r'.*\[.+\].*', path) is not None


# status: need refine and add Windows support.
def is_hidden(path):
    if path in ['.', '..', './', '../']:
        return False

    return path.startswith('.') or path.endswith('~')


def is_file(path, followlinks=True):
    if os.path.isfile(path):
        return True
    elif os.path.islink(path) and followlinks:
        return os.path.isfile(find_link_orig(path))
    else:
        return False


def is_dir(path, followlinks=True):
    if os.path.isdir(path):
        return True
    elif os.path.islink(path) and followlinks:
        return os.path.isdir(find_link_orig(path))
    else:
        return False


def is_link(path):
    return os.path.islink(path)
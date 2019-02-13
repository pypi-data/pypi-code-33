#!/usr/bin/env python
# encoding: utf-8

import os
import pickle
import tempfile


def read_to_list(path_to_file: str, comment: str = '#'):
    """
    Read the file, and returns a list of the valid lines.

    :param str path_to_file: /path/to/file
    :param str comment: Allow comment, ignore the lines which is starts with '#' as default
    :return: list
    """
    rows = list()

    if os.path.exists(path_to_file):
        for _line in open(path_to_file).readlines():
            _line = _line.strip()
            if _line:
                if comment:
                    if not _line.startswith(comment):
                        rows.append(_line)
                else:
                    rows.append(_line)

        return rows

    import cli_print as cp
    cp.error('"{}" does not exist.'.format(path_to_file))
    return rows


def cache_filename(key: str):
    """
    Generate full path to file via key.

    :param str key: key name
    :return: str
    """
    return os.path.join(tempfile.gettempdir(), '{}.pickle'.format(key))


def cache_to_file(key: str, data):
    """
    Cache a key to file.

    :param str key: key name
    :param data: value
    :return: str
    """
    path_to_file = cache_filename(key)

    with open(path_to_file, 'wb') as fp:
        pickle.dump(data, fp)

    return path_to_file


def read_cache_from_file(key: str, default=None, remove: bool = False):
    """
    Read cache from file.

    :param str key: key name
    :param default: default value
    :param bool remove: whether remove the file
    :return:
    """
    path_to_file = cache_filename(key)

    if not os.path.exists(path_to_file):
        return default

    with open(path_to_file, 'rb') as fp:
        data = pickle.load(fp)

    if remove:
        os.remove(path_to_file)

    return data

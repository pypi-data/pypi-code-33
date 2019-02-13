#!/usr/bin/env python
# encoding: utf-8

import os


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

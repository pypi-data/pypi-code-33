#!/usr/bin/env python
# encoding: utf-8

import os


def get_list_from(path_to_file: str, comment: str = '#'):
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


def read_to_list(path_to_file: str, comment: str = '#'):
    return get_list_from(path_to_file=path_to_file, comment=comment)


def put_list_to(path_to_file: str, lines: list):
    """
    Write a list to a file in lines.

    :param str path_to_file: /path/to/file
    :param list lines: source list
    :return: str
    """
    with open(path_to_file, 'w') as fp:
        content = list()
        for line in lines:
            content.append('{}'.format(line))
        fp.write('\n'.join(content))
    return path_to_file

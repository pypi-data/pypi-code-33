# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/19 09:30
import functools
import sys


def _add_indent(lines, space_cnt):
    """
    add blank before message

    :param lines: lines to be operated
    :type lines: Iterable of str

    :param space_cnt: space number
    :type space_cnt: int

    :return: lines with each started with space_cnt blanks
    """
    s = lines.split('\n')
    # don't do anything for single-line stuff
    if len(s) == 1:
        return lines
    first = s.pop(0)
    s = [(space_cnt * ' ') + line for line in s]
    s = '\n'.join(s)
    s = first + '\n' + s
    return s


"""
Whether enable message out or not
"""
_enable = True


def it_print(message=None, indent=0, device=1, newline=True):
    """
    in time print: print one line to console immediately

    :param message: the message to be printed
    :type message: object

    :param indent: number of blank to be indented, default 0
    :type indent: int

    :param device: stdout -> 1, stderr -> 2, default 1
    :type device: int

    :param newline: whether to append a new line, default True
    :type newline: bool
    """
    global _enable
    if not _enable:
        return

    if message is None:
        message = ''
    message = ' ' * indent + str(message)

    if device == 2:
        device = sys.stderr
    elif device == 1:
        device = sys.stdout
    else:
        # a file-like object
        pass

    device.write(message)
    if newline:
        device.write('\n')
    device.flush()


def it_prints(message=None, indent=0, indent_inner=2, device=1, newline=True):
    """
    in time print multiple lines: first indent with indent blanks, then every line is indented with indent_inner blanks
    """
    if message is not None:
        message = _add_indent(message, indent_inner)
    it_print(message, indent=indent, device=device, newline=newline)


def _set_enabled(enable):
    global _enable
    _enable = enable


def is_print_enable():
    """
    get the current printable status
    """
    return _enable


def set_print_enable():
    _set_enabled(True)


def set_print_disable():
    _set_enabled(False)


class disable_print(object):
    def __init__(self):
        self.prev = is_print_enable()

    def __enter__(self):
        set_print_disable()

    def __exit__(self, *args):
        _set_enabled(self.prev)
        return False

    def __call__(self, func):
        @functools.wraps(func)
        def decorate_disable_print(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return decorate_disable_print


class enable_print(object):
    def __init__(self):
        self.prev = is_print_enable()

    def __enter__(self):
        set_print_enable()

    def __exit__(self, *args):
        _set_enabled(self.prev)
        return False

    def __call__(self, func):
        @functools.wraps(func)
        def decorate_disable_print(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return decorate_disable_print

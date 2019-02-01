# -*- coding: utf-8 -*-

__author__ = 'sv99'

from datetime import datetime
import struct


def read_uint(data, pos):
    result = struct.unpack('<L', data[pos: pos + 4])
    return result[0]


def read_ushort(data, pos):
    result = struct.unpack('<H', data[pos: pos + 2])
    return result[0]


def read_datetime(data, pos):
    timestamp = read_uint(data, pos)
    return datetime.fromtimestamp(timestamp)


def read_string(data, pos):
    string = ''
    while data[pos] != 0:
        res = chr(data[pos])
        string += res
        pos += 1
    return pos + 1, string


def sizeof_fmt(num, suffix='b'):
    for unit in ['','K','M']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'G', suffix)
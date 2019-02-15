# -*- coding:utf-8 -*-

import six
import os

__all__ = ['filesize']


def filesize(f):
    """Return the size of f in bytes"""
    if isinstance(f, six.string_types):
        return os.path.getsize(f)
    else:
        # For file-like object
        now_pos = f.tell()
        f.seek(0, 2)
        size = f.tell()
        f.seek(now_pos)
        return size

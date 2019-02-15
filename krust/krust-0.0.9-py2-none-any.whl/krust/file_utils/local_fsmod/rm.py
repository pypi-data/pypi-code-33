# -*- coding:utf-8 -*-

import six
import os
import shutil
import glob
from ..path import *

__all__ = ['RM']


def _rm_one_file(path):
    if is_link(path):
        os.unlink(path)
    elif is_dir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


def RM(path):
    if path in ['/', '/*']:
        return

    fnames = glob.glob(path)
    for fn in fnames:
        try:
            _rm_one_file(fn)
        except Exception as e:
            six.print_(e)



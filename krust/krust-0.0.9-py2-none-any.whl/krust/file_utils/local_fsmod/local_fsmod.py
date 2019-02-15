# -*- coding:utf-8 -*-

import six
import os
import re
import glob
import shutil
from krux.regex import grep, simple_pattern_to_regex
from krux.converters.string_related import dict2str

from ..fsmod import FSMod
from ..path import *
from .list_file import *
from .copy_file import *
from .mkdir import MKDIR
from .rm import RM

__all__ = ['LocalFSMod']


class LocalFSMod(FSMod):
    schema = None
    name = 'local'

    def ls(self, root=None, **kwargs):
        return LS(root=root, **kwargs)

    def ls_grep(self, root=None, pattern=None, **kwargs):
        return LS_GREP(root=root, pattern=pattern, **kwargs)

    def ls_group(self, root=None, pattern=None, **kwargs):
        return LS_GROUP(root=root, pattern=pattern, **kwargs)

    def exists(self, path):
        return os.path.exists(path)

    def mkdir(self, dir_path, **kwargs):
        return MKDIR(dir_path, **kwargs)

    def rm(self, path):
        return RM(path)

    def cp(self, src, dest):
        return CP(src, dest)

    def mv(self, src, dest):
        return shutil.move(src, dest)

    def ln(self, src, dest):
        src = P(src)
        dest = P(dest)
        both_dirs = src.endswith('/') and dest.endswith('/')
        if src != '/':
            src = src.rstrip('/')
        if not both_dirs and (dest.endswith('/') or os.path.isdir(dest)):
            true_dest = os.path.join(dest, BASENAME(src))
        else:
            true_dest = dest.rstrip('/')
        MKDIR(DIRNAME(true_dest))
        if os.path.exists(true_dest):
            RM(true_dest)
        os.symlink(src, true_dest)

    def du(self, path):
        """disk usage
        part of this code comes from monkut (http://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python)
        """
        total_size = 0
        if is_dir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                total_size += os.path.getsize(dirpath)
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
        else:
            total_size = os.path.getsize(path)
        return total_size

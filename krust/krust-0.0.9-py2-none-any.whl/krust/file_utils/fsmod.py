# -*- coding:utf-8 -*-

import six
from krux.types import Null

__all__ = ['FSMod']


class FSMod(object):
    manager = Null
    schema = None
    cp_sets = []
    mv_sets = []

    def __init__(self, **kwargs):
        for k, v in six.iteritems(kwargs):
            self.__dict__[k] = v

    def ls(self, root, **kwargs):
        raise NotImplementedError

    def ls_grep(self, root=None, pattern=None, **kwargs):
        pass

    def ls_group(self, root=None, pattern=None, **kwargs):
        pass

    def exists(self, path):
        raise NotImplementedError

    def mkdir(self, dir_path, **kwargs):
        raise NotImplementedError

    def rm(self, path):
        raise NotImplementedError

    def cp(self, src, dest):
        raise NotImplementedError

    def mv(self, src, dest):
        raise NotImplementedError

    def ln(self, src, dest):
        raise NotImplementedError

    def du(self, path):
        raise NotImplementedError

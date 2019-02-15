# -*- coding:utf-8 -*-

import six
from collections import OrderedDict
from krux.types import Singleton, is_seq
import re

from .local_fsmod import LocalFSMod

__all__ = [
    'FSManager', 'fsman',
    'LS', 'LS_R', 'LS_GREP', 'LS_GROUP',
    'EXISTS',
    'MKDIR',
    'RM',
    'CP', 'MV', 'LN',
    'DU'
]


class FSManager(Singleton):
    _inited = False
    _mods = OrderedDict()
    _schema_mapping = {}

    def __init__(self):
        if not self._inited:
            self._inited = True

    def register_mod(self, mod):
        mod.manager = self
        self._mods[mod.name] = mod
        if mod.schema is None or isinstance(mod.schema, six.string_types):
            self._schema_mapping[mod.schema] = mod.name
        elif is_seq(mod.schema):
            for s in mod.schema:
                self._schema_mapping[s] = mod.name

    def find_mod(self, path, return_name=False):
        if path is None:
            mod_name = self._schema_mapping[None]
        else:
            m = re.match(r'^(?P<schema>[^\s:/]+://).*', path)
            if not m:
                mod_name = self._schema_mapping[None]
            else:
                mod_name = self._schema_mapping[m.group('schema')]

        if return_name:
            return mod_name
        else:
            return self._mods[mod_name]

    def ls(self, root=None, **kwargs):
        return self.find_mod(root).ls(root=root, **kwargs)

    def ls_grep(self, root=None, pattern=None, **kwargs):
        return self.find_mod(root).ls_grep(root=root, pattern=pattern, **kwargs)

    def ls_group(self, root=None, pattern=None,  **kwargs):
        return self.find_mod(root).ls_grep(root=root, pattern=pattern, **kwargs)

    def exists(self, path):
        return self.find_mod(path).exists(path)

    def mkdir(self, dir_path):
        return self.find_mod(dir_path).mkdir(dir_path)

    def rm(self, path):
        return self.find_mod(path).rm(path)

    def du(self, path):
        return self.find_mod(path).du(path)

    def cp(self, src, dest):
        return self._bi_op('cp', src, dest)

    def mv(self, src, dest):
        return self._bi_op('mv', src, dest)

    def ln(self, src, dest):
        return self._bi_op('ln', src, dest)

    def _bi_op(self, op, src, dest):
        src_fs = self.find_mod(src, return_name=True)
        dest_fs = self.find_mod(dest, return_name=True)
        if src_fs == dest_fs:
            return getattr(self._mods[src_fs], op)(src, dest)
        else:
            for mod in self._mods.values():
                if (src_fs, dest_fs) in getattr(mod, '{}_sets'.format(op)):
                    method_name = '{}_{}_{}'.format(op, src_fs, dest_fs)
                    if hasattr(mod, method_name) and callable(getattr(mod, method_name)):
                        return getattr(mod, method_name)(src, dest)
                    else:
                        return getattr(mod, op)(src, dest)

        raise NotImplementedError("{} {} -> {}".format(op, src_fs, dest_fs))


fsman = FSManager()
fsman.register_mod(LocalFSMod())

LS = fsman.ls
EXISTS = fsman.exists
MKDIR = fsman.mkdir
RM = fsman.rm
CP = fsman.cp
MV = fsman.mv
LN = fsman.ln
DU = fsman.du

LS_GREP = fsman.ls_grep
LS_GROUP = fsman.ls_group


def LS_R(root=None, **kwargs):
    kwargs.pop('recursive', None)
    return LS(root=root, recursive=True, **kwargs)

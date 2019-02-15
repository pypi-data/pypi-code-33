# -*- coding:utf-8 -*-

import six
import os

from .file_utils import *


class Pather(object):
    def __init__(self, env_var=None, paths=[]):
        self.paths = []
        if env_var:
            env_paths = os.environ.get(env_var, None)
            if env_paths:
                env_paths = env_paths.split(':')
                self.append(env_paths)
        self.append(paths)

    def __getitem__(self, key):
        for path in reversed(self.paths):
            if key.startswith('/'):
                return key
            fullpath = os.path.join(path, key)
            if os.path.exists(fullpath):
                return fullpath

        raise KeyError(u"Cannot find {} in paths: {}".format(key, self.paths))

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def append(self, path):
        if isinstance(path, six.string_types):
            paths = [path]
        else:
            paths = path

        for p in paths:
            self.paths.append(P(p))

    def ls(self):
        results = []
        for path in self.paths:
            fnames = LS_R(path, base_only=False)
            results.extend(fnames)
        return results

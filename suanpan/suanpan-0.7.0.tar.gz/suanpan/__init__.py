# coding=utf-8
from __future__ import print_function

import copy
import itertools


class Context(object):
    def __init__(self, **kwargs):
        self._dict = kwargs
        self.__dict__.update(
            {k: Context(**v) if isinstance(v, dict) else v for k, v in kwargs.items()}
        )

    def __getitem__(self, key):
        return self._dict[key]

    def __contains__(self, key):
        return key in self._dict

    def __len__(self):
        return len(self._dict)

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self._dict)

    def __repr__(self):
        return str(self)

    def get(self, key, default=None):
        return self._dict.get(key, default)

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()

    def to_dict(self):
        return copy.copy(self._dict)


class Global(Context):
    def set(self, key, value):
        setattr(self, key, value)
        self._dict[key] = value

    def update(self, globals={}, **kwargs):
        for key, value in itertools.chain(globals.items(), kwargs.items()):
            self.set(key, value)


g = Global()

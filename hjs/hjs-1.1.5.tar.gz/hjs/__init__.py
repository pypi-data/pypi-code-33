# coding: utf-8
"""
A thin wrapper around [hjson](http://github.com/hjson/hjson-py).
>>> from __future__ import unicode_literals
>>> from hjs import hjs, dumps, loads, dump, load
>>> da = loads('''
... {
...    a: 1
...    b: are you ok with it ?
...    t: {
...        a: you get the point, now :-)
...    },
...    values: 42
... }
... ''')
>>> assert da['values'] == 42
>>> assert da.t.a == "you get the point, now :-)"

>>> "hum, what if i put an é in this ?"
'hum, what if i put an é in this ?'
"""
from __future__ import unicode_literals
import hjson

from functools import wraps
from collections import OrderedDict
import six
import sys
PY36 = sys.version_info[:2] >= (3, 6)

if PY36:
    BaseDict = dict
else:
    BaseDict = OrderedDict

from .version import __version__  # noqa: F401


class hjs(BaseDict):
    """
    TODO ;-)
    """
    _strict = False

    def __init__(self, *args, **kwargs):
        try:
            super(hjs, self).__init__(*args, **kwargs)
        except ValueError:
            if args and isinstance(args[0], six.string_types):
                super(hjs, self).__init__()
                base = loads(args[0])
                self.update(base)
                self.update(kwargs)
            else:
                raise

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            if self.__class__._strict:
                raise AttributeError(name)
            return None

    def __setattr__(self, name, value):
        if name.startswith('_'):
            self.__dict__[name] = value
        else:
            self.__setitem__(name, value)

    def __dir__(self):
        return self.keys()


class shjs(hjs):
    _strict = True


def adapt_loader(fun, strict=False):
    @wraps(fun)
    def with_my_object_pairs_hook(*args, **kwds):
        hook = kwds.get('object_pairs_hook')
        if hook is None or hook in (BaseDict, OrderedDict):
            kwds['object_pairs_hook'] = shjs if strict else hjs
        return fun(*args, **kwds)

    return with_my_object_pairs_hook


loads = adapt_loader(hjson.loads)  # noqa: F401
load = adapt_loader(hjson.load)    # noqa: F401
sloads = adapt_loader(hjson.loads, strict=True)  # noqa: F401
sload = adapt_loader(hjson.load, strict=True)    # noqa: F401


def dumps(obj, human=False, **kw):
    if human:
        return hjson.dumps(obj, **kw)
    else:
        return hjson.dumpsJSON(obj, **kw)


def dump(obj, fp, human=False, **kw):
    if human:
        return hjson.dump(obj, fp, **kw)
    else:
        return hjson.dumpsJSON(obj, fp, **kw)

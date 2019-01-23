methods = {}


def register(name=""):
    def inner(f):
        n = name or f.__name__
        methods[n] = f
        return f
    return inner

from .loc import *
from .glob import *

def derivative(x, y, kind="finitediff", **kwargs):
    method = methods.get(kind)
    f = lambda y: method(x, y, **kwargs)
    if len(y.shape) > 1:
        return np.apply_along_axis(f, 0, y)
    else:
        return f(y)

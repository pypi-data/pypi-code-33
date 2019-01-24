import functools
import numpy as np
import math


def take(l, inds):
    if isinstance(l, np.ndarray):
        return l[inds]
    else:
        return [l[i] for i in inds]


def lazy_property(f):
    attribute = '_cache_' + f.__name__

    @property
    @functools.wraps(f)
    def decorator(self):
        if not hasattr(self, attribute):
            setattr(self, attribute, f(self))
        return getattr(self, attribute)

    return decorator


def shuffled(x, y=None):
    inds = np.random.permutation(len(x))
    if y is None:
        return take(x, inds)
    else:
        return take(x, inds), take(y, inds)


def calc_num_batch(num_data, batch_size):
    return int(math.ceil(num_data / batch_size))



def applied(iterator, f):
    for x in iterator:
        yield f(x)

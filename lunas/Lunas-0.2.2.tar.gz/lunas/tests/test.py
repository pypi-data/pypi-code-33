import copy
import time

from lunas.iterator import Iterator
from lunas.readers import Zip as Zip, Range, Shuffle


def get_reader():
    r = Range(11, buffer_size=1000).select(lambda x: x + 0)
    r2 = Range(11, buffer_size=1000).select(lambda x: 0)
    r = Zip([r, r2], buffer_size=100).select(lambda x: x)
    r = Shuffle(r, 50).select(lambda x: x).where(lambda x: x[0] < 50)
    return r


def build_it(r):
    it = Iterator(r, 3, cache_size=21, sample_size_fn=lambda x: 1)
    return it


state = None


def f():
    r = get_reader()
    it = build_it(r)

    ii = it(lambda: it.step < 3)
    rv = []
    stop = 1
    for i, b in enumerate(ii):
        rv.append((it.epoch, it.step_in_epoch, it.step, b[0].samples))
        if i == stop:
            global state
            state = copy.deepcopy(it.state_dict())

    return rv[stop + 1:]


def g():
    r = get_reader()

    it = build_it(r)
    global state
    it.load_state_dict(state)

    ii = it(lambda: it.step < 3)
    rv = []
    for i, b in enumerate(ii):
        rv.append((it.epoch, it.step_in_epoch, it.step, b[0].samples))
    return rv


tic = time.time()
a = f()
print(time.time() - tic)

tic = time.time()
b = g()
print(time.time() - tic)

assert a == b
# r = get_reader()
# it = build_it(r)
# for i in it.iter_epoch():
#     print(it.epoch,it.step_in_epoch,it.step,i[0].samples)
#
# for i in it.iter_epoch():
#     print(it.epoch, it.step_in_epoch, it.step, i[0].samples)
# for i in r:
#     pass

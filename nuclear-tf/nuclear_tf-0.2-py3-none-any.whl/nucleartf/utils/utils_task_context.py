import time
from contextlib import contextmanager


class ImmediateSkipException:
    pass


@contextmanager
def task(blockname='Noname', debug=False):
    if debug:
        print('%s start.' % blockname)
        s = time.time()

    yield

    if debug:
        e = time.time()
        print('%s end. Took %.2fs' % (blockname, e - s))

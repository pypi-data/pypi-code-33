#!/usr/bin/env python3


# see https://stackoverflow.com/questions/34988692/python-3-multiprocessing-optimal-chunk-size
def get_chunksize(size, ncpu, taskpt, chunkpt=10000):  # taskpt & chunkpt are expressed in microseconds
    return min(_div(chunkpt, taskpt), _div(size, ncpu))


def _div(x, y):
    return x // y + min(1, x % y)

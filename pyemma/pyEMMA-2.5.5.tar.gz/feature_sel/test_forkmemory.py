#!/usr/bin/env python
import psutil
from multiprocess import Pool
import numpy as np

x = np.zeros(int(1024 ** 3 / 8))
print('mem size in mb:', x.nbytes / 1024**2)

def func(i):
    print(id(x))

if __name__ == '__main__':
    # 1GB in data
    n = 2
    parent = psutil.Process()
    print(parent, parent.memory_full_info())
    with Pool(n) as p:
        tasks = [p.apply_async(func, [i] ) for i in range(n)]
        [t.get() for t in tasks]
        children = parent.children(recursive=True)
        for c in children:
            print(c, c.memory_full_info())

    #for i in range(n):
    #    assert x[i] == i, i

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import partial
import timeit

import jax.numpy as np
from jax import jit
import jax.interpreters.xla as xla

sizes = list(map(int, [1e3, 5e3, 1e4, 2e4, 5e4, 1e5, 5e5, 1e6, 2e6, 5e6]))
fun = jit(np.sum)


print("                xfer time      inst time")
for n in sizes:
  x = np.zeros(n)

  # warmup
  _ = fun(x)

  # xfer time
  xla.xfer = True
  xfer_time = timeit.timeit(lambda: fun(x), number=100) / 100.

  # inst time
  xla.xfer = False
  inst_time = timeit.timeit(lambda: fun(x), number=100) / 100.

  print("n = {} {:12.4f}  {:11.4f}".format(str(n).ljust(8), xfer_time, inst_time))


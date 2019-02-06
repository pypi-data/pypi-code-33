from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import partial
from timeit import default_timer

import numpy as np
from jax import lax
from jax import jit
from jax import numpy as jax_numpy
from jax import random as jax_random

n_list = [1e3, 5e3, 1e4, 2e4, 5e4, 1e5, 5e5, 1e6, 2e6]
n_list = [int(i) for i in n_list]


key = jax_random.PRNGKey(0)
print("             Compile time   ( per 1k n)   Run time")
for n in n_list:
  x = np.arange(n, dtype=np.int32)
  key, subkey = jax_random.split(key)

  start_time = default_timer()
  # y = jax_random.shuffle(subkey, x)
  y = jax_random.uniform(subkey, [n])
  run_and_compile_time = default_timer() - start_time

  key, subkey = jax_random.split(key)

  start_time = default_timer()
  # z = jax_random.shuffle(subkey, x)
  z = jax_random.uniform(subkey, [n])
  run_time = default_timer() - start_time

  approx_compile_time = run_and_compile_time - run_time

  print("n = {} {:12.4f}  {:11.4f}    {:8.4f}".format(
      str(n).ljust(8), approx_compile_time, approx_compile_time / n * 1000,
      run_time))


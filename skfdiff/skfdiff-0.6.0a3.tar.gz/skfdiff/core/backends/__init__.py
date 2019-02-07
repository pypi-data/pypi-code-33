#!/usr/bin/env python
# coding=utf-8

import warnings
from .base_backend import get_backend, available_backends

try:
    from .numba_backend import NumbaBackend
except ImportError:
    warnings.warn("Numba cannot be imported: numba backend will not be available.")

from .numpy_backend import NumpyBackend

# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

import sys
import warnings

if (3, 5) <= sys.version_info < (3, 6):
    warnings.warn(
        "Support for Python 3.5 will be removed in tron-api-python",
        category=DeprecationWarning,
        stacklevel=2)

if sys.version_info < (3, 5):
    raise EnvironmentError(
        "Python 3.5 or above is required. "
        "Note that support for Python 3.5 will be remove in  tron-api-python")

import pkg_resources

from eth_account import Account  # noqa: E402
from tronapi.main import Tron  # noqa: E402
from tronapi.providers.http import (
    HttpProvider,  # noqa: E402
)

__version__ = pkg_resources.get_distribution("tronapi").version

__all__ = [
    "__version__",
    "Tron",
    "HttpProvider",
    "Account"
]

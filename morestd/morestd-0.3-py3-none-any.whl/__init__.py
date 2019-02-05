#
# morestd: More standard libraries for Python
#
# Copyright 2010-2018 Ferry Boender, released under the MIT license
#

_version_str = '0.3'
version = [int(v) for v in _version_str.split(".")]

from . import time   # noqa
from . import fs     # noqa
from . import file   # noqa
from . import shell  # noqa
from . import net    # noqa
from . import data   # noqa
from . import lsb    # noqa

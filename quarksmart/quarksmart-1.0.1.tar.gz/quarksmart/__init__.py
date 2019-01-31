# -*- coding: utf-8 -

from .quarksmart import *
from .settings import version_info

__version__ = ".".join([str(v) for v in version_info])
SERVER_SOFTWARE = "quarksmart/%s" % __version__

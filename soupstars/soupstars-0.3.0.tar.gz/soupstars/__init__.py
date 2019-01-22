"""
Soupstars

~ Parse the web like a rockstar
"""

__version__ = "0.2.0"

import os

from .config import SoupstarsConfig
from .loaders import BaseLoader, DefaultLoader, HttpLoader
from .caches import BaseCache, DefaultCache, FilesystemCache, RedisCache
from .readers import BaseReader, DefaultReader, HttpReader
from .parsers import BaseParser, HttpParser
from .utils import parse, iter_parsers

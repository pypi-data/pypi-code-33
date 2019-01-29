# -*- coding: utf-8 -*-

"""Top-level package for pydnameth."""
# flake8: noqa

__author__ = """Aaron Blare"""
__email__ = 'aaron.blare@mail.ru'
__version__ = '0.1.6'

from . import config
from .config import *
from . import model
from .model import *

__all__ = config.__all__
__all__.extend(model.__all__)

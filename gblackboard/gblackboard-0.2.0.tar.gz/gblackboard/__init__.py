# -*- coding: utf-8 -*-

"""Top-level package for gblackboard."""

__author__ = """G.Ted"""
__email__ = 'gted221@gmail.com'
__version__ = '0.2.0'


from .exception import (
    BlackboardException,
    UnsupportedMemoryType,
    DataException,
    MemoryException,
    NotCallable,
    KeyNotString,
    UnsupportedDataType,
    ExistingKey,
    NotEditable,
    NonExistingKey,
    RedisException,
    RedisWrongConfig,
    RedisNotConnected
)

from .wrapper import SupportedMemoryType
from .gblackboard import Blackboard

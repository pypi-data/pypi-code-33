# coding=utf-8

from enum import Enum


class ModeEnum(Enum):
    """Enumerator describing the optimization training strategy."""
    MIN = 0
    MAX = 1
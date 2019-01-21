# Standard Library
import enum


__all__ = ("Params", "sentinel")


class Params(enum.Enum):
    sentinel = enum.auto()


sentinel = Params.sentinel

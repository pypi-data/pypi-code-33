"""Basic data storage class"""
# vim: set expandtab ts=4 sw=4:

from .abstract import AbstractAnam
from .register import register_class

__all__ = []


class Store(AbstractAnam):
    """
    A placeholder object which can have everything placed into extra_data
    such that it can be serialised in and out simply.

    Often used for storing things which don't need their own dedicated class.
    """

    def __init__(self):
        AbstractAnam.__init__(self)

    def __eq__(self, other):
        seenkeys = {}
        for k in list(self.extra_data.keys()):
            seenkeys[k] = 1
            if k in other.extra_data:
                if self.extra_data[k] != other.extra_data[k]:
                    return False
            else:
                return False

        for k in list(other.extra_data.keys()):
            if k not in seenkeys:
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)


__all__.append('Store')
register_class(Store)

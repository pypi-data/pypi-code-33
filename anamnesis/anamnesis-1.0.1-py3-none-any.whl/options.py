#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

from sys import stdout

__all__ = []


class AnamOptions(object):
    """
    Singleton class for holding system-wide options
    """

    __shared_state = {}

    def __init__(self, *args, **kwargs):
        # Quick way of implementing a singleton
        self.__dict__ = self.__shared_state

        if not getattr(self, 'initialised', False):
            self.initialised = True
            self.setup(*args, **kwargs)

    def setup(self):
        self.verbose = 0
        self.progress = 0

    def write(self, s, target=stdout):
        if self.verbose > 0:
            target.write(s)

    def write_progress(self, s, target=stdout):
        if self.progress > 0:
            target.write(s)


__all__.append('AnamOptions')

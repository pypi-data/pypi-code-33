#!/usr/bin/python

# This file should be loaded during the register tests

from ..abstract import AbstractAnam
from ..register import register_class


class NameMapTestCase(AbstractAnam):

    hdf5_outputs = ['_classvarname']

    hdf5_mapnames = {'_classvarname': 'filevarname'}

    def __init__(self):
        AbstractAnam.__init__(self)

        self._classvarname = 'foo'


__all__ = ['NameMapTestCase']
register_class(NameMapTestCase)

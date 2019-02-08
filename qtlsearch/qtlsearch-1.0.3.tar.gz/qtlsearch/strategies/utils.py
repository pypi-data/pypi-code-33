#!/usr/bin/env python
'''
    QTLSearch — to search for candidate causal genes in QTL studies
     by combining Gene Ontology annotations across many species, leveraging
    hierarchical orthologous groups.

    (C) 2015-2018 Alex Warwick Vesztrocy <alex@warwickvesztrocy.co.uk>

    This file is part of QTLSearch. It contains utilities for strategies.

    QTLSearch is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    QTLSearch is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with QTLSearch.  If not, see <http://www.gnu.org/licenses/>.
'''
from .. import __packagename__
from importlib import import_module


class Strategy(object):
    def __init__(self):
        self.strategy = None
        self.args = {}

    @property
    def is_set(self):
        return self.strategy is not None

    def set_strategy(self, strategy):
        self.strategy = import_module('.strategies.{}'.format(strategy),
                                      package=__packagename__)
        self.args = {}

    def get_strategy(self):
        assert self.is_set, 'No strategy set.'

        return self.strategy

    def save_args(self, keys, args):
        for key in keys:
            self.args[key] = getattr(args, key)


STRATEGY = Strategy()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remark annotations.
"""
import inspect

from metabeyond import remarks

from ricochet import scopes


class Objectlet(remarks.Remark, constraint=inspect.isfunction):
    """
    Marks a method in a configuration that should be invoked to obtain an objeclet.

    Keyword Args:
        scope:
            The scope to initialise the objectlet as. Defaults to `singleton`.
        lazy:
            If true, the objectlet is not initialised until it is first autowired in by something else.
            If false, as per the default, then it will be initialised immediately.
    """

    def __init__(self, *, scope: scopes.Scope = scopes.Scope.SINGLETON, lazy: bool = False):
        super().__init__()
        self.scope = scope
        self.lazy = lazy

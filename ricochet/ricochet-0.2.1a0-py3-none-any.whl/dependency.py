#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Represents a resolvable dependency.
"""
from typing import Any, Type

from ricochet.utils import hints


@hints.abstract_class
@hints.slotted
class BaseDependencyDescriptor:
    """Represents the base interface for a dependency descriptor."""

    __slots__ = ()

    def __init__(self):
        if type(self) == BaseDependencyDescriptor:
            raise TypeError()


@hints.slotted
class ObjectletDependencyDescriptor(BaseDependencyDescriptor):
    """
    Represents a dependency to resolve.
    """

    __slots__ = ('name', 'type')

    def __init__(self, *, name: str, type: Type[Any]) -> None:
        super().__init__()
        self.name = name
        self.type = type

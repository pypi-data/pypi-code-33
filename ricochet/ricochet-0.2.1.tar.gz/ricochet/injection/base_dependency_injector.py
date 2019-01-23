#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency injector base class.
"""
__all__ = ['BaseDependencyInjector']

import abc
from typing import Any, Iterator

from ricochet import dependency, exceptions
from ricochet.utils import hints


@hints.interface
class BaseDependencyInjector(abc.ABC):
    """
    Interface specification for an entity with the ability to resolve and inject dependencies into objects.
    """

    @abc.abstractmethod
    def resolve_dependencies(self, object: Any) -> None:
        """
        Resolves any autowired dependencies in the given object.

        Args:
            object:
                The object to resolve dependencies for.
        """
        raise exceptions.AbstractError

    @abc.abstractmethod
    def get_dependencies(self, object: Any) -> Iterator[dependency.BaseDependencyDescriptor]:
        """
        Returns an iterator across any dependencies in the given object that need to be resolved.
        """
        raise exceptions.AbstractError

    @abc.abstractmethod
    def wire_in_objectlet(self, object: Any, name: str, objectlet: Any) -> None:
        """
        Wire in the given objectlet to the given object under the given name.

        Args:
            object:
                the object to inject the dependency into.
            name:
                the name of the objectlet dependency.
            objectlet:
                the objectlet dependency itself.
        """
        raise exceptions.AbstractError

    @abc.abstractmethod
    def get_objectlet_from_dependency(
        self, dependency_descriptor: dependency.ObjectletDependencyDescriptor
    ) -> Any:
        """
        Takes an objectlet dependency descriptor and attempts to get the objectlet from a registry matching that
        definition.

        Args:
            dependency_descriptor:
                The description of the dependency to locate.

        Returns:
            The dependency.
        """
        raise exceptions.AbstractError

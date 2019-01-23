#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency injector implementation.
"""
__all__ = ['DependencyInjector']

from typing import Any, Iterator

from ricochet import autowired
from ricochet import dependency
from ricochet import objectlet_registries
from ricochet.utils import logger_mixin

from . import base_dependency_injector


class DependencyInjector(base_dependency_injector.BaseDependencyInjector, logger_mixin.LoggerMixin):
    """
    Basic implementation of a dependency injector,
    """

    def __init__(self, registry: objectlet_registries.BaseRegistry):
        super().__init__()
        self.registry = registry

    def resolve_dependencies(self, object: Any) -> None:
        dependencies = self.get_dependencies(object)
        for dependency_descriptor in dependencies:
            if isinstance(dependency_descriptor, dependency.ObjectletDependencyDescriptor):
                objectlet = self.get_objectlet_from_dependency(dependency_descriptor)
                self.wire_in_objectlet(object, dependency_descriptor.name, objectlet)
            else:
                raise NotImplementedError(
                    f'No handler for {type(dependency_descriptor).__name__} is implemented yet.'
                )

    def get_dependencies(self, object: Any) -> Iterator[dependency.BaseDependencyDescriptor]:
        all_annotations: dict = getattr(type(object), '__annotations__', {})

        for name, annotation in all_annotations.items():
            if isinstance(annotation, type) and issubclass(annotation, autowired.Autowired):
                self.logger.debug('Discovered requirement %r in %s', name, object)
                yield dependency.ObjectletDependencyDescriptor(name=name)

    def wire_in_objectlet(self, object: Any, name: str, objectlet: Any) -> None:
        self.logger.debug('Autowiring %r into %s', name, object)
        setattr(object, name, objectlet)

    def get_objectlet_from_dependency(
        self, dependency_descriptor: dependency.ObjectletDependencyDescriptor
    ) -> Any:
        canonical_name = self.registry.get_canonical_name_for(dependency_descriptor.name)
        return self.registry.get_objectlet(canonical_name)

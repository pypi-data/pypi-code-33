#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wraps a prototype and singleton registry and provides a managed unified interface to both at the same time.
"""
__all__ = ["BaseDualRegistryMediator"]

import abc
from typing import Iterator, Any, Type

from ricochet import exceptions, scopes
from ricochet.utils import hints
from . import base_prototype_registry, base_singleton_registry


@hints.abstract_class
class BaseDualRegistryMediator(
    base_prototype_registry.BasePrototypeRegistry,
    base_singleton_registry.BaseSingletonRegistry,
    abc.ABC,
):
    """
    This abstracts prototype and singleton objectlet_registries to provide a system that allows access to both types of objectlet_registries
    using the same methods in an expected way. This functions by overriding conflicting implementations.
    """

    def __init__(self):
        super().__init__()

    def contains_objectlet_named(self, canonical_name: str) -> bool:
        """
        Args:
            canonical_name:
                The canonical object name. This is the primary name the object is registered under and resolved by.
                This implements no form of alias lookup.

        Returns:
            `True` if a prototype or singleton with the canonical name is registered, `False` if not.
        """
        singleton = self.contains_singleton_named(canonical_name)
        prototype = self.contains_prototype_named(canonical_name)

        return singleton or prototype

    def contains_objectlets_typed(self, type: Type[Any]) -> bool:
        """
        Args:
            type:
                A class that a prototype or singleton is expected to be derived from.

        Returns:
            `True` if any prototype or singleton derived from the given type exists, `False` if not.
        """
        singleton = self.contains_singletons_typed(type)
        prototype = self.contains_prototypes_typed(type)

        return singleton or prototype

    def count_objectlets_named(self, canonical_name: str) -> int:
        """
        Args:
            canonical_name:
                The canonical object name. This is the primary name the object is registered under and resolved by.
                This implements no form of alias lookup.

        Returns:
            A count of object instances, if the prototype or singleton exists for that name.

        Raises:
            NameError if no prototype or singleton exists with that name.
        """
        # We can safely make the assumption that
        # >>> assert singleton_count ^ prototype_count
        # if we use the basic implementation rules, but user implementations may do voodoo type shit, so
        # we may as well cater for that and it makes the operation terse.
        prototypes = self.count_instances_of_prototype_named(canonical_name)
        singleton = 1 if self.contains_singleton_named(canonical_name) else 0
        return prototypes + singleton

    def is_objectlet(self, candidate_object: Any) -> bool:
        """
        Args:
            candidate_object: The potential singleton or prototype instance to look for.

        Returns:
            `True` if this object is a prototype instance or a singleton object in this registry, or `False` otherwise.
        """
        return self.is_prototype_instance(candidate_object) or self.is_singleton(candidate_object)

    def get_all_canonical_objectlet_names(self) -> Iterator[str]:
        """
        Yields all object names. These are expected to be unique as long as the internal representations that are
        protected have not been tampered with directly.
        """
        yield from self.get_all_singleton_names()
        yield from self.get_all_prototype_names()

    ########################
    # Overridden functions #
    ########################

    def register_new_prototype(self, canonical_name: str, prototype: Any) -> None:
        """
        Registers the given object as a prototype under the given name.

        Args:
           canonical_name:
               The canonical prototype's name. This is the primary name the object is registered under and resolved by.
           prototype:
               The object itself to register.

        Throws:
           ValueError:
               if the prototype is `None`.
           NameError:
               if the prototype is already registered as a singleton or prototype.
        """
        if canonical_name in self.get_all_singleton_names():
            raise exceptions.ObjectletIsAlreadyRegisteredError(
                canonical_name, scopes.Scope.SINGLETON
            )
        elif canonical_name in self.get_all_prototype_names():
            raise exceptions.ObjectletIsAlreadyRegisteredError(
                canonical_name, scopes.Scope.PROTOTYPE
            )
        else:
            return super().register_new_prototype(canonical_name, prototype)

    def register_new_singleton(self, canonical_name: str, singleton: Any) -> None:
        """
        Registers the given object as a singleton under the given name.

        Args:
           canonical_name:
               The canonical singleton's name. This is the primary name the object is registered under and resolved by.
           singleton:
               The object itself to register.

        Throws:
           :class:`ValueError`:
               if the singleton is `None`.
           :class:`NameError`:
               if the singleton is already registered as a singleton or prototype
        """
        if canonical_name in self.get_all_singleton_names():
            raise exceptions.ObjectletIsAlreadyRegisteredError(
                canonical_name, scopes.Scope.SINGLETON
            )
        elif canonical_name in self.get_all_prototype_names():
            raise exceptions.ObjectletIsAlreadyRegisteredError(
                canonical_name, scopes.Scope.PROTOTYPE
            )
        else:
            return super().register_new_singleton(canonical_name, singleton)

    def get_objectlet(self, canonical_name: str) -> Any:
        singleton = self.get_singleton_named(canonical_name)
        if singleton is not None:
            return singleton

        prototype = self.create_instance_of_prototype(canonical_name)
        if prototype is not None:
            return prototype

        raise exceptions.ObjectletNotFoundError(canonical_name)

    def register_new_objectlet(self, canonical_name: str, object: Any, scope: scopes.Scope):
        if scope is scopes.Scope.SINGLETON:
            self.register_new_singleton(canonical_name, object)
        elif scope is scopes.Scope.PROTOTYPE:
            self.register_new_prototype(canonical_name, object)
        else:
            raise NotImplementedError(
                f'Scope {scope.name} is not implemented for this type of registry'
            )

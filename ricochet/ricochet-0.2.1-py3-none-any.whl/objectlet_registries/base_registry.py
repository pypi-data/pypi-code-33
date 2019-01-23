#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Represents a generic registry. This is an ABC that an application context can be expected to interface with.

There is no requirement to implement all of the methods, only some need to be implemented. This is designed to allow
a Singleton registry and a Prototype registry to interop together, or for only one implementation to be used.
"""

__all__ = ["BaseRegistry"]

import abc
from typing import Iterator, Type, Any, Optional

from ricochet import exceptions, scopes
from ricochet.utils import hints, logger_mixin


@hints.abstract_class
class BaseRegistry(abc.ABC, logger_mixin.LoggerMixin):
    """
    A generic type of registry that is expected to be the interface used in an application. A registry is some
    form of collection of objects that are managed by this framework, and are thus known as objectlets. This acts as
    a form of "objectlet repository" for dependency injection components that require access to a collection of
    objectlets at runtime under a restricted and managed interface.

    The importance of this to be managed in a correct way is increased with the dynamic and non-encapsulated nature
    of Python code.
    """

    def __init__(self):
        super().__init__()
        #: Maps aliases to names.
        self._aliases = {}

    @abc.abstractmethod
    def get_objectlet(self, canonical_name: str) -> Any:
        """
        Gets the given objectlet with the given canonical name, and type.

        Args:
            canonical_name:
                The objectlet's canonical name to find.

        Returns:
            The located objectlet.

        Raises:
            NameError if the objectlet cannot be found.
        """
        raise exceptions.AbstractError

    @abc.abstractmethod
    def register_new_objectlet(self, canonical_name: str, object: Any, scope: scopes.Scope) -> None:
        """
        Register a new objectlet as a given scope under the given canonical name.

        Args:
            canonical_name:
                The objectlet's canonical name to be registered under.
            object:
                The objectlet to register.
            scope:
                The scope to use for the object when resolving it.

        Raises:
            :cls:`exceptions.ObjectletIsAlreadyDefined` if an objectlet already exists with this name.
            :cls:`ValueError` if the given object is `None`.
        """
        raise exceptions.AbstractError

    @abc.abstractmethod
    def contains_objectlet_named(self, canonical_name: str) -> bool:
        """
        Args:
            canonical_name:
                The canonical objectlet name. This is the primary name the objectlet is registered under and resolved
                by. This implements no form of alias lookup.

        Returns:
            `True` if a prototype or singleton with the canonical name is registered, `False` if not.
        """
        raise exceptions.AbstractError

    @abc.abstractmethod
    def contains_objectlets_typed(self, type: Type[Any]) -> bool:
        """
        Args:
            type:
                A class that a prototype or singleton is expected to be derived from.

        Returns:
            `True` if any prototype or singleton derived from the given type exists, `False` if not.
        """
        raise exceptions.AbstractError

    @abc.abstractmethod
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
        raise exceptions.AbstractError

    @abc.abstractmethod
    def is_objectlet(self, candidate_object: Any) -> bool:
        """
        Args:
            candidate_object: The potential singleton or prototype instance to look for.

        Returns:
            `True` if this object is a prototype instance or a singleton objectlet in this registry, or `False`
            otherwise.
        """
        raise exceptions.AbstractError

    @abc.abstractmethod
    def get_all_canonical_objectlet_names(self) -> Iterator[str]:
        """
        Yields all objectlet names. These are expected to be unique as long as the internal representations that are
        protected have not been tampered with directly.
        """
        raise exceptions.AbstractError

    def get_all_objectlet_names(self) -> Iterator[str]:
        """
        Returns:
            The same as :attr:`get_all_canonical_objectlet_names`, but also any stored aliases. The order of these
            is not defined, and should not be relied upon.
        """
        yield from self.get_all_canonical_objectlet_names()
        yield from self._aliases

    def get_canonical_name_for(self, alias: str) -> Optional[Any]:
        """
        Looks up an alias or canonical name and returns the matching canonical name for an objectlet.

        Args:
            alias:
                any alias for an objectlet.

        Returns:
            The alias input if it is already a canonical name (primary name for an objectlet). If it is a valid
            alias, the canonical name will always be returned. If the alias is not registered, then we instead return
            None.
        """
        if alias in self.get_all_canonical_objectlet_names():
            return alias

        try:
            return self._aliases[alias]
        except KeyError:
            return None

    def get_aliases_for(self, alias: str) -> Iterator[str]:
        """
        Gets the aliases for a given canonical name or alias as an iterator.

        Args:
            alias:
                The canonical name or alias to look up

        Returns:
            An iterator across all aliases. This does not include the canonical name. If no alias with the provided
            name exists, then no result will be yielded.

            To determine if an alias exists, one should use the :meth:`get_canonical_name_for` method instead.
        """
        canonical_name = self.get_canonical_name_for(alias)
        if canonical_name is not None:
            for alias, name in self._aliases.items():
                if name == canonical_name:
                    yield alias

    def get_names_for(self, alias: str) -> Iterator[str]:
        """
        Args:
            alias:
                Alias or canonical name to look up.

        Returns:
            An iterator across all canonical and object names for the given alias/canonical name. If no match
            is found, then no items are yielded. This order is arbitrary.
        """
        canonical_name = self.get_canonical_name_for(alias)
        if canonical_name is not None:
            yield canonical_name
            yield from self.get_aliases_for(canonical_name)

    def register_alias(self, new_alias, existing_alias) -> None:
        """
        Registers an alias to an existing object alias, thus allowing it to be referred to by the new alias
        additionally.

        Args:
            new_alias:
                The new alias to register and use to refer to an object.
            existing_alias:
                The name of the existing object to apply the new alias to. This may be an alias or a canonical name.

        Throws:
            ValueError if the existing alias does not exist.
            NameError if the new alias already exists.
        """

        if new_alias in self.get_all_objectlet_names():
            canonical_name = self.get_canonical_name_for(new_alias)
            # Assume this always matches, this just helps provide a decent error message.
            raise exceptions.ObjectletAliasIsAlreadyTakenError(
                new_alias, existing_alias, canonical_name
            )
        else:
            canonical_name = self.get_canonical_name_for(existing_alias)
            if canonical_name is None:
                raise exceptions.ObjectletNotFoundError(existing_alias)
            else:
                self._aliases[new_alias] = canonical_name

    def contains_objectlet_with_alias(self, candidate_name: str) -> bool:
        """
        Return true if the name is an alias, but not a canonical name.
        """
        return candidate_name in self.get_aliases_for(candidate_name)

    def contains_objectlet_with_canonical_name(self, candidate_name: str) -> bool:
        """
        Return true if the name is a valid canonical name.
        """
        return candidate_name in self.get_all_canonical_objectlet_names()

    @property
    def alias_count(self) -> int:
        """
        Number of registered aliases not including canonical names.
        """
        return len(self._aliases)

    @property
    def name_count(self) -> int:
        """
        Number of registered aliases and canonical names.
        """
        return sum(1 for _ in self.get_all_objectlet_names())

    @property
    def objectlet_count(self) -> int:
        """
        Returns:
            The number of objectlets that are managed.
        """
        return sum(1 for _ in self.get_all_canonical_objectlet_names())

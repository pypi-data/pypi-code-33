#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Singleton registry implementation that uses normal references.
"""
__all__ = ["SingletonRegistry"]

from typing import Any, Dict, ItemsView, Iterator, KeysView, Optional, Type, ValuesView

from ricochet.objectlet_registries import base_singleton_registry
from ricochet.utils import logger_mixin


class SingletonRegistry(base_singleton_registry.BaseSingletonRegistry, logger_mixin.LoggerMixin):
    """
    Basic implementation of a Singleton registry. This provides access to any singleton objectlets as normal references,
    as the simplest implementation.
    """

    def __init__(self):
        super().__init__()
        self._singletons: Dict[str, Any] = {}

    def contains_singleton_named(self, canonical_name: str) -> bool:
        return canonical_name in self._singletons

    def contains_singletons_typed(self, type: Type[Any]) -> bool:
        iterator = self.get_singletons_typed(type)
        try:
            next(iterator)
        except StopIteration:
            return False
        else:
            return True

    def get_singleton_named(self, canonical_name: str) -> Optional[Any]:
        if canonical_name in self._singletons:
            return self._singletons[canonical_name]
        else:
            return None

    def get_singletons_typed(self, type: Type[Any]) -> Iterator[Any]:
        yield from (obj for obj in self._singletons.values() if isinstance(obj, type))

    def register_new_singleton(self, canonical_name: str, singleton: Any) -> None:
        if singleton is None:
            raise ValueError("Cannot register a NoneType singleton")
        elif canonical_name in self._singletons:
            raise NameError("Singleton is already registered")
        else:
            self.logger.debug(
                "Registering singleton %r from %s-typed %r",
                canonical_name,
                type(singleton).__name__,
                singleton,
            )
            self._singletons[canonical_name] = singleton

    def is_singleton(self, candidate_singleton: Any) -> bool:
        # This is expected to be a proxy only.
        return candidate_singleton in self._singletons.values()

    def get_all_singletons(self) -> ItemsView[str, Any]:
        return self._singletons.items()

    def get_all_singleton_names(self) -> KeysView[str]:
        return self._singletons.keys()

    def get_all_singleton_instances(self) -> ValuesView[Any]:
        return self._singletons.values()

    @property
    def singleton_count(self) -> int:
        return len(self._singletons)

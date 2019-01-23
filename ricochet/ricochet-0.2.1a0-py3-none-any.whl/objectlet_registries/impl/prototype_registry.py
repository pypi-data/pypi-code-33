#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prototype registry implementation that uses normal references.
"""
__all__ = ["PrototypeRegistry", "PrototypeMediator"]

import copy
import weakref
from typing import Any, KeysView, Optional, Type

from ricochet.objectlet_registries import base_prototype_registry
from ricochet.utils import logger_mixin, hints


@hints.slotted
class PrototypeMediator:
    """
    Internal wrapper for a prototype which handles maintaining counts of prototypes and producing new prototypes
    via a deep-copy. Since this is slotted to reduce overhead, no ABC will be made for this interface.

    Contains a logger to use which is passed from the containing prototype registry implementation to provide
    appropriate logging under a meaningful logger name.
    """

    __slots__ = ("logger", "prototype_name", "prototype_obj", "instances")

    def __init__(self, logger, prototype_name, prototype_obj):
        #: The logger to log with.
        self.logger = logger
        #: The name of the prototype this adapter wraps.
        self.prototype_name = prototype_name
        #: The actual prototype object itself.
        self.prototype_obj = prototype_obj
        #: Weak references pointing to the instances of the :attr:`prototype_obj` prototype. This automatically
        #: destroys references to any prototype instance that has been garbage collected, so it maintains itself.
        self.instances = weakref.WeakSet()

    def __len__(self):
        return len(self.instances)

    def make_new_instance(self):
        inst = copy.deepcopy(self.prototype_obj)
        self.logger.info(
            "Created new instance of prototype %s (#%s) at #%s",
            self.prototype_name,
            id(self.prototype_obj),
            id(inst),
        )

        self.instances.add(inst)
        return inst


class PrototypeRegistry(base_prototype_registry.BasePrototypeRegistry, logger_mixin.LoggerMixin):
    """
    Basic implementation of a Prototype registry. This generates objectlets from a given prototype under a specific
    identifier, aiming to be the simplest implementation possible.

    Warning:
        This produces prototypes using deep-copy internally. This will fail to produce correct prototypes on objects
        such as strings and ints which are internally optimised as reused pooled objects in CPython.

        It will also not work on metaclasses (i.e. the type of a type).

        Weak references are used internally to maintain a total count of prototype objectlets created. This means that
        it will fail for internal types such as :class:`object` which are slotted and immutable to weakref entries
        by default.
    """

    def __init__(self) -> None:
        super().__init__()
        self._prototypes = {}

    def contains_prototype_named(self, canonical_name: str) -> bool:
        return canonical_name in self._prototypes

    def contains_prototypes_typed(self, type: Type[Any]) -> bool:
        return any(
            True
            for prototype in self._prototypes.values()
            if isinstance(prototype.prototype_obj, type)
        )

    def create_instance_of_prototype(self, canonical_name: str) -> Optional[Any]:
        try:
            return self._prototypes[canonical_name].make_new_instance()
        except KeyError:
            raise NameError(f"Prototype {canonical_name} does not exist")

    def register_new_prototype(self, canonical_name: str, prototype: Any) -> None:
        if prototype is None:
            raise ValueError("Cannot register a NoneType prototype")
        elif canonical_name in self._prototypes:
            raise NameError("Prototype is already registered")
        else:
            self.logger.debug(
                "Registering prototype %r as %s-typed %r",
                canonical_name,
                type(prototype).__name__,
                prototype,
            )

            self._prototypes[canonical_name] = PrototypeMediator(
                self.logger, canonical_name, prototype
            )

    def is_prototype_instance(self, candidate_prototype_instance: Any) -> bool:
        return any(
            candidate_prototype_instance in prototype_header.instances
            for prototype_header in self._prototypes.values()
        )

    def count_instances_of_prototype_named(self, canonical_name: str) -> int:
        if canonical_name in self._prototypes:
            return len(self._prototypes[canonical_name])
        else:
            raise NameError(f"No prototype named {canonical_name!r} exists")

    def get_all_prototype_names(self) -> KeysView[str]:
        return self._prototypes.keys()

    @property
    def prototype_count(self) -> int:
        return len(self._prototypes)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementation of a :class:`ricochet.objectlet_registries.prototype_and_singleton_registry.BaseDualRegistryMediator`
that uses the basic prototype registry and basic singleton registry internally.
"""
__all__ = ["DualRegistryMediator"]

from ricochet.objectlet_registries import base_dual_registry_mediator
from ricochet.objectlet_registries.impl import prototype_registry, singleton_registry


class DualRegistryMediator(
    base_dual_registry_mediator.BaseDualRegistryMediator,
    prototype_registry.PrototypeRegistry,
    singleton_registry.SingletonRegistry,
):
    """
    Implements the `BaseDualRegistryMediator` wrapper of a `PrototypeRegistry` and a `SingletonRegistry`.
    """

    pass

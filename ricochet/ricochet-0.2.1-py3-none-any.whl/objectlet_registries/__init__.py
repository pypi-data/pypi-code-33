#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Defines base registry interfaces for Singleton and Prototype objectlet_registries. These are the core starting points for the
entire organisation implemented by this framework.

Keeping definitions simple, assuming you understand object orientation concepts:
    **Singletons**:
        Global objects created once and shared. Often these refer to classes that may only ever have one instance,
        whereas in this framework, it refers to an object with a specific name. Zero or more managed components
        may store a reference to zero or more singleton instances. If one component changes the state of a singleton,
        then this change seen by all components that store a reference to the same singleton.

    **Prototypes**:
        An object which is stored internally by the registry once. Each component that requests a reference to the
        prototype will receive some object created from the state of the prototype. Changing this object will not
        mutate the original prototype in any way, and thus provides a copy to every component that requires one.

        This is very similar to a normal instance, but instead of using a class to create an object, we use an
        existing object to derive a copy from.

        Likewise, these are much more difficult to track, as there is no implementation for tracking instances
        created from prototypes.

Registries manage a collection of objects. The objectlet_registries here contain implementations to replicate and distribute
singleton or prototype objects. These are used elsewhere in this framework for autowiring, etc.
"""
from .base_dual_registry_mediator import *
from .base_prototype_registry import *
from .base_registry import *
from .base_singleton_registry import *
from .impl.dual_registry_mediator import *
from .impl.prototype_registry import *
from .impl.singleton_registry import *

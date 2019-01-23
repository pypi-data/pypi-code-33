#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base exceptions used in this framework.
"""
from ricochet import scopes


class RicochetError(RuntimeError):
    """
    Base runtime error for Ricochet.
    """

    def __init__(self, message: str, *args, **kwargs):
        error_message = message.format(*args, **kwargs)
        self.error_message = error_message

    def __repr__(self):
        return f'<{type(self).__name__}: {self.error_message!r}>'

    def __str__(self):
        return self.error_message


class AbstractError(RicochetError):
    """
    Raised if an accessed element is abstract.
    """

    def __init__(self):
        super().__init__('This element is abstract and should be overridden to be used')


class ObjectletManagementError(RicochetError):
    """
    Base for any objectlets that fail to load.
    """

    pass


class ObjectletNotFoundError(ObjectletManagementError):
    """
    Raised if an Objectlet cannot be resolved because it does not exist.
    """

    def __init__(self, objectlet_name: str):
        super().__init__('Objectlet {} does not exist in the registry', objectlet_name)


class ObjectletIsAlreadyRegisteredError(ObjectletManagementError):
    """
    Raised if an Objectlet under the given signature already exists.
    """

    def __init__(self, objectlet_name: str, scope: scopes.Scope):
        super().__init__(
            'Objectlet {} already exists as a {} in this registry',
            objectlet_name,
            scope.name.lower(),
        )


class ObjectletAliasIsAlreadyTakenError(ObjectletManagementError):
    """
    Raised when registering an alias if the alias is already taken.
    """

    def __init__(self, desired_alias: str, canonical_name: str, taken_by_name: str):
        super().__init__(
            'Cannot register alias {} to {} as it is already taken by {}',
            desired_alias,
            canonical_name,
            taken_by_name,
        )

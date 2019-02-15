""" This module contains exceptions for :py:class:`~save_to_db.core.scope.Scope`
class.
"""

class ScopeException(Exception):
    """ General exception for :py:class:`~save_to_db.core.scope.Scope` class.
    """

class ScopeDoesNotExist(ScopeException):
    """ Raised when trying to get a scope that does not exist. """


class ItemClsAlreadyScoped(ScopeException):
    """ Raised when an already scoped item is scoped again. """


class ScopeIdAlreadyInUse(ScopeException):
    """ Raised when trying to use the same `scope_id` twice. """
    
    
class ScopeIdCannotBeNone(ScopeException):
    """ Raised when trying to set `scope_id` to `None`. """
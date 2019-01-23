""" This module contains exceptions for
:py:class:`~save_to_db.core.item.Item` class configuration. These
exceptions are only raised when an item configuration is correct in its
structure but cannot be used, for example, when a nonexistent relation is used.
If, for example, a boolean value was used instead of a list, general exception
will be raise when trying to deal with a boolean as with a list.
"""

class ItemConfigError(Exception):
    """ General exception for configuration of
    :py:class:`~save_to_db.core.item.Item` class.
    """

class InvalidFieldName(ItemConfigError):
    """ Raised when configuration uses model field name that has double
    underscores in it.
    """

class RelatedItemNotFound(ItemConfigError):
    """ Raised when:
    
        - A related item was specified using a string path but no item
          class was found using the path.
        - During auto configuration of
          :py:class:`~save_to_db.core.item.Item` class relations, when no
          item was found for a specific model class.
    """

class MultipleRelatedItemsFound(ItemConfigError):
    """ Raised when:
    
        - A related item was specified using a string path with an
          item class name only and there are no such class in the
          referencing item
          module but more then one in other modules.
        - During auto configuration of
          :py:class:`~save_to_db.core.item.Item` relations, when more then one
          item was found for a specific model class.
    """

class ItemAdapterNotFound(ItemConfigError):
    """ Raised when an adapter for a particular item class was not found
    during class setup.
    """

class NonExistentRelationDefined(ItemConfigError):
    """ Raised when relation is set for a field that does not exist or is not
    a foreign key field in corresponding model.
    """

class NonExistentFieldUsed(ItemConfigError):
    """ Raised when `getters`, `creators`, or `nullables` contains field name
    that `model_cls` does not have.
    """
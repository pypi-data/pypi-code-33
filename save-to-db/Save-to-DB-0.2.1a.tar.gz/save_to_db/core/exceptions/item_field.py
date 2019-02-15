""" This module contains exceptions for
:py:class:`~save_to_db.core.item_base.ItemBase` related to fields usage.
"""


class ItemFieldError(ValueError):
    """ General exception for :py:class:`~save_to_db.core.item_base.ItemBase`
    field usage.
    """

class WrongAlias(ItemFieldError, KeyError):
    """ Raise when wrong alias is used. """


class BulkItemOnetoXDefaultError(ItemFieldError):
    """ Raised when trying to assing an one-to-x default relationship value
    to a bulk item.
    """
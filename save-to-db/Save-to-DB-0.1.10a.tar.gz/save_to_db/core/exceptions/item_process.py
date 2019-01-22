""" This module contains exceptions that are raise when there is an error
processing an item.
"""

class ItemProcessError(Exception):
    """ General exception for processing instances of
    :py:class:`~save_to_db.core.item_base.ItemBase` class.
    """


class ItemsNotTheSame(ItemProcessError):
    """ Raised when trying to merge items that cannot be merged during
    processing items in a bulk item that can potentially refer to
    the same record in a database.
    """


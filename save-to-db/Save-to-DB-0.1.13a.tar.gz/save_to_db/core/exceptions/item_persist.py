""" This module contains exceptions for
:py:class:`~save_to_db.core.item_base.ItemBase` class related to persistence.
"""


class ItemPersistError(Exception):
    """ General exception for :py:class:`~save_to_db.core.item_base.ItemBase`
    persistence.
    """
    
    def __repr__(self):
        result = ''
        for arg in self.args:
            if result: 
                result = '{}, {}'.format(result, str(arg))
            else:
                result = str(arg)
        return result


class MultipleItemsMatch(ItemPersistError):
    """ Raised when multiple items match the same model. Applicable to bulk
    items.
    """
    
    
class MultipleModelsMatch(ItemPersistError):
    """ Raised when multiple models match the same item:
        
        - When `allow_multi_update` set to `False` for the item.
        - When trying to set multiple items to x-to-one relationship.
    """

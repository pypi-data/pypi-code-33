import json
from pprint import pprint
from .utils.selector import select
from .utils.dict_wrapper import DictWrapper



class ItemBase(object):
    """ This is an abstract item class that serves as a base class for
    single item and bulk item classes.
    
    .. seealso::
        :py:class:`~.item.Item` and :py:class:`~.bulk_item.BulkItem` classes.
    
    :param \*\*kwargs: Values that will be saved as item data.
    """
    
    #--- special methods -------------------------------------------------------
    
    def __init__(self, **kwargs):
        self.complete_setup()

        self.data = {}
        for key, value in kwargs.items():
            item = self
            real_keys = self._get_real_keys(key)
            i = -1
            for i, real_key in enumerate(real_keys[:-1]):
                if item.is_bulk_item():
                    i -= 1
                    break
                item = item[real_key]
            
            remaining_key = '__'.join(real_keys[i+1:])
            if not isinstance(value, list):
                item[remaining_key] = value
            else:
                item[remaining_key].add(*value)
                
    
    def __setitem__(self, key, value):
        raise NotImplementedError()
    
    
    def __call__(self, **kwargs):
        for key, value in kwargs.items():
            self[key] = value
        return self
        
    
    def __getitem__(self, key):
        raise NotImplementedError()
    
    
    def __delitem__(self, key):
        raise NotImplementedError()
    
    
    def __contains__(self, key):
        raise NotImplementedError()
    
    
    #--- utility methods -------------------------------------------------------
         
    def to_dict(self):
        """ Converts item into a Python `dict` object.

        :returns: Python `dict` representation of the item.
        """
        raise NotImplementedError()
    
    
    def dict_wrapper(self):
        """ This method is used for integration with Scrapy project, when
        parsing pages in Scrapy you can yield an item as
        :py:class:`~.utils.dict_wrapper.DictWrapper` (subclass of `dict`)
        and then use :py:meth:`~.utils.dict_wrapper.DictWrapper.get_item`
        method to get the original item.
        
        :returns: An :py:class:`~.utils.dict_wrapper.DictWrapper` class
            instance.
        """
        return DictWrapper(self)
    
    
    def load_dict(self, data):
        """ Loads data from dictionary into the item.
        
        :param data: Dictionary with item data (see :func:`~to_dict` method).
        :returns: The item itself.
        """
        raise NotImplementedError()
    
    
    #--- helper functions ------------------------------------------------------
    
    def pprint(self, as_json=None, width=None):
        """ Pretty prints the item. """
        if width is None and as_json is None:
            as_json = True
        
        if not as_json:
            pprint(self.to_dict(), width=width if width else 80)
        else:
            print(json.dumps(self.to_dict(), indent=4, sort_keys=True))
    
    
    def select(self, key):
        """ Just calls :py:func:`~.utils.selector.select` function from
        :py:mod:`save_to_db.core.utils.selector` module with `self` as the first
        argument.
        
            .. seealso::
                :py:func:`save_to_db.core.utils.selector.select` function.
        """
        return select(self, key)
    
    
    #--- main methods ----------------------------------------------------------
    
    def as_list(self):
        """ Returns a list of items. For single items simply returns a list 
        containing only `self`, for bulk items returns list of all items.  
        """
        raise NotImplementedError()
    
    
    def is_single_item(self):
        """ Returns `True` if item is a single item. """
        raise NotImplementedError()
    
    
    def is_bulk_item(self):
        """ Returns `True` if item is a bulk item. """
        raise NotImplementedError()
    
    
    def process(self):
        """ Converts all set string values to the appropriate data types and
        sets default values if needed.
        """
        raise NotImplementedError()
    
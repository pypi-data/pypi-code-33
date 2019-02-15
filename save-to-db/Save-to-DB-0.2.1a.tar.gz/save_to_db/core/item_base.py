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
    
    def pprint(self, as_json=True, *args, **kwargs):
        """ Pretty prints the item.
        
        :param as_json: If `True` (default), the a JSON representation of item
            is printed, otherwise dictionary representation is printed using
            `pprint` method from `pprint` module.
        :param \*args: These arguments passed to `pprint.pprint` function or to
            `json.dumps`.
        :param \**kwargs: These key-value arguments passed to `pprint.pprint`
            function or to `json.dumps`.
        """
        
        if not as_json:
            if 'width' not in kwargs:
                kwargs['width'] = 80
            pprint(self.to_dict(), *args, **kwargs)
        else:
            json_kwargs = {
                'ensure_ascii': False,
                'indent': 4,
                'sort_keys': True,
            }
            json_kwargs.update(kwargs)
            print(json.dumps(self.to_dict(), *args, **json_kwargs))
    
    def select(self, key):
        """ Just calls :py:func:`~.utils.selector.select` function from
        :py:mod:`save_to_db.core.utils.selector` module with `self` as the first
        argument.
        
            .. seealso::
                :py:func:`save_to_db.core.utils.selector.select` function.
        """
        return select(self, key)
    
    
    def get_item_cls(self):
        """ Returns class reference of a single item class that this item
        works with.
        """
        raise NotImplementedError()
    
    
    def is_scoped(self):
        """ Returns `True` if the item class is scoped """
        raise NotImplementedError()
    
    
    def get_scope_id(self):
        """ Returns ID of the scope of the item. """
        raise NotImplementedError()
    
    
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
        """ Converts all set values to the appropriate data types, sets default
        values if needed, calls `process()` method on all referenced items.
        
        :returns: Dictionary with single item classes as keys and lists of
            single item instances as values.
        """
        raise NotImplementedError()
    
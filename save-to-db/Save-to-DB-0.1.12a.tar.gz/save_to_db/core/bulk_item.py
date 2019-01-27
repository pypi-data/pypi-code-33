from copy import deepcopy, copy
from .item import ItemBase
from .item_contructor import complete_item_structure
from .exceptions import BulkItemOnetoXDefaultError


class BulkItem(ItemBase):
    """ This class deals with instances of :py:class:`~.item.Item` in chunks.
    It can create or update multiple database rows using single query, e.g. it
    can persist multiple items at once.
    
    .. warning::
        Defaults injection order is not guaranteed.
    
    :param item_cls: A subclass of :py:class:`~.item.Item` that
        this class deals with.
    :param \*\*kwargs: Values that will be saved as **default** item data.
    """
    
    #--- special methods -------------------------------------------------------
    
    def __init__(self, item_cls, **kwargs):
        self.item_cls = item_cls
        self.bulk = []
        
        self.data = {}
        for key, value in kwargs.items():
            self[key] = value  # this will trigger `__setitem__` function
        
    
    def __setitem__(self, key, value):
        real_key = self.item_cls._get_real_keys(key)
        real_key_str = '__'.join(real_key)
        
        item_cls = self.item_cls
        for key in real_key:
            if key not in item_cls.relations:
                break
            
            relation = item_cls.relations[key]
            if relation['relation_type'].is_one_to_x():
                raise BulkItemOnetoXDefaultError(self.item_cls, key,
                                                 real_key_str)
            item_cls = relation['item_cls']
        
        self.data[real_key_str] = value
        
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.bulk[key]
        
        real_keys = self.item_cls._get_real_keys(key)
        return self._get_direct(real_keys)
    
    
    def _get_direct(self, real_keys):
        real_key = '__'.join(real_keys)
        if real_key in self.data:
            return self.data[real_key]
        
        item_cls = self.item_cls
        for real_key in real_keys:
            if real_key in item_cls.relations:
                item_cls = item_cls.relations[real_key]['item_cls']
            else:
                raise KeyError(real_key)
        
        self.data[real_key] = item_cls.__genitem(real_keys[-1])
        return self.data[real_key]
    
    
    def __delitem__(self, key):
        real_key = self.item_cls._get_real_keys(key, as_string=True)
        del self.data[real_key]
    
    
    def __contains__(self, key):
        try:
            real_keys = self.item_cls._get_real_keys(key)
        except KeyError:
            return False
        return self._contains_direct(real_keys)
    
    
    def _contains_direct(self, real_keys):
        return '__'.join(real_keys) in self.data
    
    
    def slice(self, start=0, stop=None, step=1):
        """ Returns copy of the bulk item with only certain items.
        
        :param start: Index of the first item (inclusive) in the bulk to add to
            the new bulk.
        :param stop: Index of the last item (not inclusive) in the bulk to add
            to the new bulk.
        :param step: Specifies by how much to increment index each time
            when moving from `start` to `stop`.
        """
        if stop is None:
            stop = len(self.bulk)
        new_bulk = self.item_cls.Bulk()
        new_bulk.data = copy(self.data)
        new_bulk.add(*self.bulk[start:stop:step])
        
        return new_bulk
    
    
    def __len__(self):
        return len(self.bulk)
        
    
    #--- utility methods -------------------------------------------------------
    
    def to_dict(self):
        return self._to_dict(_item_to_dict={}, _address_to_item={})
        
        
    def _to_dict(self, _item_to_dict, _address_to_item):
        self_address = id(self)
        if self_address in _item_to_dict:
            if self_address not in _address_to_item:
                _address_to_item[self_address] = len(_address_to_item) + 1
            self_id = _address_to_item[self_address]
            _item_to_dict[self_address]['id'] = self_id
            return {
                'id': self_id,
            }
        
        result = {
            'defaults': {},
            'bulk': [],
        }
        _item_to_dict[self_address] = result
        
        # defaults first in `_load_dict()` as well
        defaults = result['defaults']
        for key, value in self.data.items():
            if not isinstance(value, ItemBase):
                defaults[key] = value
            else:
                defaults[key] = value._to_dict(_item_to_dict=_item_to_dict,
                                               _address_to_item=_address_to_item)
        
        bulk = result['bulk']
        for item in self.bulk:
            bulk.append(item._to_dict(_item_to_dict=_item_to_dict,
                                      _address_to_item=_address_to_item))
        
        return result
    
    
    def load_dict(self, data):
        return self._load_dict(data, _id_to_item={})
    

    def _load_dict(self, data, _id_to_item):
        if 'id' in data:
            if data['id'] not in _id_to_item:
                _id_to_item[data['id']] = self.item_cls.Bulk()
                
            bulk = _id_to_item[data['id']]
            if 'defaults' not in data:
                return _id_to_item[data['id']]
        else:
            bulk = self.item_cls.Bulk()
        
        # defaults first in `_to_dict()` as well
        for key, value in data['defaults'].items():
            # getting relation class
            cur_cls = bulk.item_cls
            for cur_key in key.split('__'):
                if cur_key in cur_cls.relations:
                    cur_cls = cur_cls.relations[cur_key]['item_cls']
                else:
                    cur_cls = None
                    break
            if cur_cls:  # relation
                bulk[key] = cur_cls()._load_dict(value, _id_to_item)
            else:
                bulk[key] = value
        
        # bulk
        for dict_wrapper in data['bulk']:
            bulk.add(bulk.item_cls()._load_dict(dict_wrapper, _id_to_item))
        
        return bulk
    
    
    #--- properties ------------------------------------------------------------
    
    @property
    def model_cls(self):
        """ Property that returns `model_cls` attribute of the `item_cls`
        class.
        """
        return self.item_cls.model_cls
    
    def get_item_cls(self):
        return self.item_cls
    
    def is_scoped(self):
        return self.item_cls.metadata['scope_id'] != None
    
    def get_scope_id(self):
        return self.item_cls.metadata['scope_id']
    
    
    #--- main methods ----------------------------------------------------------
    
    def add(self, *items):
        """ Adds `item` to the bulk.
        
        :param \*item: List of instances of :py:class:`~.item_base.ItemBase`
            class to be added to the bulk.
        """
        for item in items:
            if item not in self.bulk:
                self.bulk.append(item)
    
    
    def gen(self, *args, **kwargs):
        """ Creates a :py:class:`~.item.Item` instance and adds it to the bulk.
        
        :param \*args: Positional arguments that are passed to the item
            constructor.
        :param \*\*kwargs: Keyword arguments that are passed to the item
            constructor.
        :returns: :py:class:`~.item.Item` instance.
        """
        item = self.item_cls(*args, **kwargs)
        self.add(item)
        return item
    
    
    def remove(self, *items):
        """ Removes `item` from the bulk.
        
        :param \*items: List of instances of :py:class:`~.item_base.ItemBase`
            class to be removed from the bulk.
        """
        for item in items:
            if item in self.bulk:
                self.bulk.remove(item)
    
    
    def as_list(self):
        return self.bulk
    
    
    def is_single_item(self):
        return False
    
    
    def is_bulk_item(self):
        return True
    
    
    def process(self):
        self._process(_procesed_items=[])
        return complete_item_structure(self)
    

    def _process(self, _procesed_items):
        if self in _procesed_items:
            return
        _procesed_items.append(self)
        
        for key, value in self.data.items():
            if not isinstance(value, ItemBase):
                self.data[key] = self.item_cls.process_field(key, value,
                                                             aliased=False)
            else:
                self.data[key]._process(_procesed_items=_procesed_items)

            for item in self.bulk:
                if key not in item:
                    item[key] = deepcopy(self.data[key])
        
        for item in self.bulk:
            item._process(_procesed_items=_procesed_items)
        
        
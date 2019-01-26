# -*- coding: utf-8 -*-
"""
Created on Sat Dec 29 08:27:13 2018

@author: yoelr
"""

class ReadOnlyBook(dict):
    """Create a read-only dictionary. ReadOnlyBook objects are hashable and immutable.

    **Parameters**

         ****kwargs:** Key-value pairs to initialize dictionary

    **Example**
    
        ReadOnlyBook objects are simply immutable and hashable dictionaries.   
        
        >>> rob = ReadOnlyBook(name='Rob', children=20)
        >>> rob['name'] = 'Yoel'
        TypeError: Cannot set items in a ReadOnlyBook object.
        >>> set((1, 2), rob)
        {(1, 2), {'name': 'Rob', 'children': 20}}
    
    """
    __slots__ = ('_hash',)
    
    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        self._hash = hash((type(self),) + tuple(self.items()))
        return self._hash

    def __setitem__(self, key, val):
        raise TypeError(f'Cannot set items in a {type(self).__name__} object.')
    
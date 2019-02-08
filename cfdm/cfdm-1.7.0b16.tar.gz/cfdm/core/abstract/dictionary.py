#from builtins import (object, str)
from future.utils import with_metaclass

import abc

from copy import deepcopy
from . import Container


class Dictionary(with_metaclass(abc.ABCMeta, Container)):
    '''<TODO>

.. versionadded:: 1.7.0

    '''
    def __contains__(self, key):
        '''
        '''
        return key in  self._dictionary()
    #--- End: def

    def __getitem__(self, key):
        '''
        '''
        return self._dictionary()[key]
    #--- End: def

    def __iter__(self):
        '''
        '''
        return iter(self._dictionary().keys())
    #--- End: def

    def __len__(self):
        '''<TODO>

.. versionadded:: 1.7.0

        '''
        return len(self._dictionary())
    #--- End: def
    
    # ----------------------------------------------------------------
    # Private methods    
    # ----------------------------------------------------------------
    @abc.abstractmethod
    def _dictionary(self, copy=False):
        '''
        '''
        raise NotImplementedError()
    #--- End: def
    
    @abc.abstractmethod
    def _set(self, key, value, copy=True):
        '''Set a property.

.. versionadded:: 1.7.0

.. seealso:: `del_property`, `get_property`, `has_property`,
             `properties`, `replace_properties`

:Parameters:

    prop: `str`
        The name of the property to be set.

    value:
        The value for the property.

    copy: `bool`, optional
        If True then set a deep copy of *value*.

:Returns:

     `None`

**Examples:**

>>> d.set('project', 'CMIP7')
>>> p.has('project')
True
>>> p.get('project')
'CMIP7'
>>> p.del('project')
'CMIP7'
>>> p.has('project')
False
>>> print(p.del('project', None))
None
>>> print(f.get_property('project', None))
None

        '''
        raise NotImplementedError()
    #--- End: def

    # ----------------------------------------------------------------
    # Private dictionary-like methods    
    # ----------------------------------------------------------------
    @abc.abstractmethod
    def _pop(self, key, *default):
        '''
        '''
        raise NotImplementedError()
    #--- End: def

    @abc.abstractmethod
    def _popitem(self):
        '''
        '''
        raise NotImplementedError()
    #--- End: def

    @abc.abstractmethod
    def _update(self, other):
        '''
        '''
        raise NotImplementedError()
    #--- End: def

    # ----------------------------------------------------------------
    # Dictionary-like methods    
    # ----------------------------------------------------------------
    def get(self, key, *default):
        '''
        '''
        try:
            return self[key]
        except KeyError as error:
            if default:
                return default[0]

            raise error
    #--- End: def
    
    def items(self):
        '''
        '''
        return self._dictionary().items()
    #--- End: def

    def keys(self):
        '''
        '''
        return self._dictionary().keys()
    #--- End: def
    
    def values(self):
        '''
        '''
        return self._dictionary().values()
    #--- End: def

#--- End: class

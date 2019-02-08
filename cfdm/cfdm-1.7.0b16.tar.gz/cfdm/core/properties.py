from builtins import super

from . import abstract

class xProperties(abstract.Dictionary):
    '''<TODO>

.. versionadded:: 1.7.0

    '''
    
    def __init__(self, properties=None, source=None, copy=True):
        '''**Initialization**

:Parameters:

    properties: `dict`, optional
        Set descriptive properties. The dictionary keys are property
        names, with corresponding values. Ignored if the *source*
        parameter is set.

        *Parameter example:*
           ``properties={'standard_name': 'altitude'}``
        
        Properties may also be set after initialisation with the
        `replace` and `set` methods.

    source: optional
        Initialize the properties from those of *source*.

    copy: `bool`, optional
        If False then do not deep copy input parameters prior to
        initialization By default parameters are deep copied.

        '''
        super().__init__()

        if source is not None:
            properties = source._dictionary(copy=copy)
        elif properties is None:
            properties = {}
        
        self._set_component('properties', properties, copy=False)
    #--- End: def

    def __call__(self, *args, **kwargs):
        '''TODO
        '''
        return self.properties
    #--- End: def
    
    def __deepcopy__(self, memo):
        '''Called by the `copy.deepcopy` standard library function.

.. versionadded:: 1.7.0

        '''
        return self.copy()
    #--- End: def
   
    def __contains__(self, key):
        '''
        '''
        return key in self._get_component('properties')
    #--- End: def
    
    def __getitem__(self, key):
        '''
        '''
        return self._get_component('properties')[key]
    #--- End: def
  
    def __iter__(self):
        '''
        '''
        return iter(self._get_component('properties').keys())
    #--- End: def'
            
    def __len__(self):
        '''<TODO>

.. versionadded:: 1.7.0

        '''
        return len(self._get_component('properties'))
    #--- End: def

    # ----------------------------------------------------------------
    # Private methods    
    # ----------------------------------------------------------------
    def _dictionary(self, copy=False):
        '''
        '''
        out = self._get_component('properties')

        if copy:
            return {key: deepcopy(value) for key, value in out.items()}
        else:
            return out.copy()
    #--- End: def

    def _set(self, prop, value, copy=True):
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

>>> p.set('project', 'CMIP7')
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
        if copy:
            value = deepcopy(value)
            
        self._get_component('properties')[prop] = value
    #--- End: def

    # ----------------------------------------------------------------
    # Private dictionary-like methods    
    # ----------------------------------------------------------------
    def _pop(self, key, *default):
        '''
        '''
        return self._get_component('properties').pop(key, *default)
    #--- End: def

    def _popitem(self):
        '''
        '''
        return self._get_component('properties').popitem()
    #--- End: def

    def _update(self, other):
        '''
        '''
        self._get_component('properties').update(other._dictionary())
    #--- End: def

    def get(key, *default):
        '''
        '''
        return self._get_component('properties').items()
    #--- End: def


    def items(self):
        '''
        '''
        return self._get_component('properties').items()
    #--- End: def
    
    def keys(self):
        '''
        '''
        return self._get_component('properties').keys()
    #--- End: def
    
    def values(self):
        '''
        '''
        return self._get_component('properties').values()
    #--- End: def

    def copy(self):
        '''Return a deep copy.

``f.copy()`` is equivalent to ``copy.deepcopy(f)``.

.. versionadded:: 1.7.0

:Returns:

        The deep copy.

**Examples:**

>>> g = f.copy()

        '''
        return type(self)(source=self, copy=True)
    #--- End: def

#--- End: class


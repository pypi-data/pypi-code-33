# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 21:54:01 2019

@author: yoelr
"""
from warnings import warn
import numpy as np
from .utils import dim
from .array import array

__all__ = ('material_array',)

ndarray = np.ndarray
asarray = np.asarray


class material_array(ndarray):
    """Create an array that issues a RuntimeWarning when a non-positive or non-finite value is encountered.

    **Parameters**

         **array:** [array_like] Input data, in any form that can be converted to an array. This includes lists, lists of tuples, tuples, tuples of tuples, tuples of lists and ndarrays.
         
         **dtype:** [data-type] By default, the data-type is inferred from the input data.
         
         **order:** {'C', 'F'} Whether to use row-major (C-style) or column-major (Fortran-style) memory representation. Defaults to ‘C’.

    **Examples**
    
        Create material_array:

        .. code-block:: python
    
            >>> arr = material_array([1, 18])
            material_array([1, 18])
           
        A negative value issues a RuntimeWarning:
           
        .. code-block:: python
         
            >>> arr[1] = -1
            __main__:1: RuntimeWarning:
            Encountered negative or non-finite value in 'material_array' object.

    """
    __slots__ = ()
    
    _units = ''
    
    @classmethod
    def enforce_valuecheck(cls, val):
        """If *val* is True, issue warning when non-finite or negative values are encountered."""
        if val:
            cls.__setitem__ = cls._setitem 
            cls.__array_wrap__ = cls._array_wrap
        else:
            cls.__setitem__ = array.__setitem__
            cls.__array_wrap__ = array.__array_wrap__

    def __new__(cls, arr, dtype=np.float64, order=None):
        self = asarray(arr, dtype, order).view(cls)
        return self

    def __setitem__(self, key, val):
        # When self[:] = self
        if val is self: return
        
        # Check values and return
        val = np.asarray(val)
        if (val < 0).any() or (val == np.inf).any():
            warn(RuntimeWarning(f"Encountered non-finite or negative value in '{type(self).__name__}' object."), stacklevel=2)
        super().__setitem__(key, val)
    
    _setitem = __setitem__
    
    def __array_wrap__(self, out_arr):
        # New array should not be a material_array
        if self is out_arr:
            if (self < 0).any() or (self == np.inf).any():
                warn(RuntimeWarning(f"Encountered non-finite or negative value in '{type(self).__name__}' object."), stacklevel=2)
        else:
            out_arr.__class__ = array
        return out_arr
    
    _array_wrap = __array_wrap__

    def __repr__(self):
        units = self._units
        if units: units = dim(f' ({units})')
        return array.__repr__(self) + units
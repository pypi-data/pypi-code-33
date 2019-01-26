# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 16:42:49 2018

This module includes classes and functions relating arrays.

@author: Guest Group
"""
import numpy as np

__all__ = ('organized_list', 'same_type_tuple',
           'same_type', 'reorder', 'get_frac', 'dim')

ndarray = np.ndarray
asarray = np.asarray
integer = np.integer

def dim(string):
    """Return string with gray ansicolor coding."""
    return '\x1b[37m\x1b[22m' + string + '\x1b[0m'


# %% Functions for array like objects

def reorder(array: 'array_like', current_order: tuple, new_order: tuple) -> np.ndarray:
    """Return a reordered array with zero in place of elements that exist in the new order but not in the current order.
    
    .. code-block:: python
       
       >>> reorder([1,2,3], ('a', 'b', 'c'), ('a', 'c', 'd', 'b'))
       array([1, 3, 0, 2])
    
    """
    n = 0
    p_new = np.zeros(len(new_order))
    for ID1 in current_order:
        m = 0
        for ID2 in new_order:
            if ID1 == ID2:
                p_new[m] = array[n]
            m += 1
        n += 1
    return p_new

def get_frac(array) -> 'Normalized array':
    """Normalize array to a magnitude of 1. If magnitude is zero, all fractions will have equal value."""
    sum_array = sum(array)
    if sum_array == 0:
        l = len(array)
        frac = np.ones(l)/l
    else:
        frac = array/sum_array
    return frac

def organized_list(iterable):
    """Return a list with iterable in alphabetical order using its string representation. Repetitions are not included."""
    iterable = sorted(set(i for i in iterable if str(i) != ''), key=lambda i: str(i))
    return iterable

def same_type_tuple(type_, iterable):
    """Return the iterable as a tuple. Raise TypeError if any item in iterable is not an instance of type_."""
    # Make sure iterable are in a tuple
    if isinstance(iterable, type_):
        iterable = (iterable,)
    else:
        iterable = tuple(iterable)    
        # Check that all are type_ instances
        for s in iterable:
            if not isinstance(s, type_):
                raise TypeError(f"Only '{type_.__name__}' objects are valid elements for ins, not '{type(s).__name__}' objects.")
    return iterable

def same_type(iterable, type_):
    """Raise TypeError if any item in iterable is not an instance of type_."""
    # Make sure iterable are in a tuple
    if not isinstance(iterable, type_):
        # Check that all are type_ instances
        for s in iterable:
            if not isinstance(s, type_):
                raise TypeError(f"Only '{type_.__name__}' objects are valid elements, not '{type(s).__name__}' objects.")


                
                
import weakref

try:
    # Optional import for numpy types
    import numpy as np
except: # pragma: no cover
    pass

__all__ = [
    'enum_property',
    'bool_property',
    'str_property',
    'index_property',
    'weakref_property',
    'array_property',
    'lookup_property',
    'func_property',
]


TRUE_VALUES = {True, 'true', 'True', 'TRUE', 1}
FALSE_VALUES = {False, 'false', 'False', 'FALSE', 0}


def _property_name(name):
    """
    Returns the property name string.

    Parameters
    ----------
    name : str
        The name of the property to be created.
    """
    if not isinstance(name, str):
        raise ValueError('Property name {!r} must be a string.'.format(name))

    return '_{}'.format(name)


def enum_property(name, iterable):
    """
    Creates a class property that has an iterable qualifier. If the value
    assigned to the property is not contained in the qualifying iterable,
    an exception is raised. To use, place the method within a class's scope.

    Parameters
    ----------
    name : str
        The name of the property to be created.
    iterable : iterable
        An iterable, such as a tuple, list, set, dictionary, or generator.
        If a dictionary, the value will be checked against the dictionary
        keys. For faster validation times on large iterables, the use of a
        set is recommended over a tuple or list.

    Examples
    --------
    >>> class Class():
    ...     property1 = bool_property('property1', {'apples', 'oranges'})
    """
    name = _property_name(name)

    def fget(self):
        return getattr(self, name)

    def fset(self, value):
        if value not in iterable:
            raise ValueError('{} property {}:: Value {!r} not in {!r}.'
                .format(type(self).__name__, name[1:], value, iterable))
        setattr(self, name, value)

    def fdel(self):
        delattr(self, name)

    return property(fget=fget, fset=fset, fdel=fdel)


def bool_property(name):
    """
    Creates a class property that has a boolean value input qualifier.
    To use, place the method within a class's scope.

    The values `{True, 'true', 'True', 'TRUE', 1}` will be interpreted as True
    when set to the property, while the values `{False, 'false', 'False', 'FALSE', 0}`
    will be interpreted as False. All other values will raise an exception.

    Parameters
    ----------
    name : str
        The name of the property to be created.

    Examples
    --------
    >>> class Class():
    ...     bool1 = bool_property('bool1')
    """
    name = _property_name(name)

    def fget(self):
        return getattr(self, name)

    def fset(self, value):
        if value in TRUE_VALUES:
            value = True
        elif value in FALSE_VALUES:
            value = False
        else:
            raise ValueError('{} property {}:: Value {!r} not convertible '
                'to boolean.'.format(type(self).__name__, name[1:], value))
        setattr(self, name, value)

    def fdel(self):
        delattr(self, name)

    return property(fget=fget, fset=fset, fdel=fdel)


def str_property(name):
    """
    Creates a class property that is restricted to string values.
    All values set to the property will be converted to strings via `str()`.
    If that is not possible, an exception will be raised.
    To use, place the method within a class's scope.

    Parameters
    ----------
    name : str
        The name of the property to be created.

    Examples
    --------
    >>> class Class():
    ...     str1 = str_property('str1')
    """
    name = _property_name(name)

    def fget(self):
        return getattr(self, name)

    def fset(self, value):
        if not isinstance(value, str):
            value = str(value)
        setattr(self, name, value)

    def fdel(self):
        delattr(self, name)

    return property(fget=fget, fset=fset, fdel=fdel)


def index_property(index):
    """
    Creates a named setter and getter for an object that is a subclass of
    a list or array. To use, place the method within a class's scope.

    Parameters
    ----------
    name : str
        The name of the object
    index : int
        The index associated with the name.

    Examples
    --------
    The following could be done to map a 2D array to names [x, y]:

    >>> class Class(list):
    ...     x = index_property('x', 0) # obj.x can be used in lieu of obj[0]
    ...     y = index_property('y', 1) # obj.y can be used in lieu of obj[1]
    ...
    ...     def __init__(self, x, y):
    ...         self.extend([x, y])
    """
    def fget(self):
        return self[index]

    def fset(self, value):
        self[index] = value

    return property(fget=fget, fset=fset)


def weakref_property(name):
    """
    Creates a class property with a weak reference. To use, place the method
    within a class's scope.

    Parameters
    ----------
    name : str
        The name of the property to be created.

    Examples
    --------
    >>> class Class():
    ...     property1 = weakref_property('property1')
    """
    name = _property_name(name)

    def fget(self):
        value = getattr(self, name)

        if value is None:
            return value

        return value()

    def fset(self, value):
        if value is not None:
            value = weakref.ref(value)
        setattr(self, name, value)

    def fdel(self):
        delattr(self, name)

    return property(fget=fget, fset=fset, fdel=fdel)


def array_property(name, **kwargs):
    """
    Creates a class property that converts input data to a NumPy array.
    To use, place the method within the class's scope.

    Parameters
    ----------
    name : str
        The name of the property to be created.
    kwargs
        Keyword arguments that will be passed to :func:`numpy.asarray`.

    Examples
    --------
    >>> class Class():
    ...     property1 = array_property('property1', dtype='float')
    """
    name = _property_name(name)

    def fget(self):
        return getattr(self, name)

    def fset(self, value):
        value = np.asarray(value, **kwargs)
        setattr(self, name, value)

    def fdel(self):
        delattr(self, name)

    return property(fget=fget, fset=fset, fdel=fdel)


def lookup_property(name, lookup):
    """
    Creates a class property that looks up data from a supplied dictionary.
    To use, place the method within the class's scope.

    Parameters
    ----------
    name : str
        The name of the property to be created.
    lookup : dict
        The dictionary used for lookups.

    Examples
    --------
    >>> class Class():
    ...     LOOKUP_DICT = {'x': 1, 'y': 2, 'z': 3}
    ...     property1 = lookup_property('property1', LOOKUP_DICT)
    """
    name = _property_name(name)

    # Validate lookup
    if not isinstance(lookup, dict):
        raise ValueError('Lookup object must be a dictionary, not type {}.'
            .format(type(lookup).__name__))

    def fget(self):
        return getattr(self, name)

    def fset(self, value):
        if value not in lookup:
            raise ValueError('{} property {}:: Value {!r} not in {}.'
                .format(type(self).__name__, name[1:], value, list(lookup)))
        value = lookup[value]
        setattr(self, name, value)

    def fdel(self):
        delattr(self, name)

    return property(fget=fget, fset=fset, fdel=fdel)


def func_property(name, lookup=None):
    """
    Creates a class property that is restricted to a callable object.
    To use, place the method within the class's scope.

    Parameters
    ----------
    name : str
        The name of the property to be created.
    lookup : dict
        The dictionary used for lookups if the input value is not callable.
        If None, an exception will be raised if the object is not callable.

    Examples
    --------
    >>> class Class():
    ...     property1 = func_property('property1')
    """
    name = _property_name(name)

    # Validate lookup
    if lookup is not None and not isinstance(lookup, dict):
        raise ValueError('Lookup object must be a dictionary, not type {}.'
            .format(type(lookup).__name__))

    def fget(self):
        return getattr(self, name)

    def fset(self, value):
        if not callable(value):
            if lookup is None:
                raise ValueError('{} property {}:: Value {!r} is not callable.'
                    .format(type(self).__name__, name[1:], value))
            elif value not in lookup:
                raise ValueError('{} property {}:: Value {!r} is not in {}.'
                    .format(type(self).__name__, name[1:], value, lookup))
            value = lookup[value]
        setattr(self, name, value)

    def fdel(self):
        delattr(self, name)

    return property(fget=fget, fset=fset, fdel=fdel)

import pytest
from .properties import *


def func(x): # pragma: no cover
    return x


class PropTestClass(list):
    LOOKUP_DICT = {'x': 1, 'y': 2, 'z': 3}
    FUNC_DICT = {'x': func}

    enum_prop = enum_property('enum_prop', {'apple', 'orange'})
    bool_prop = bool_property('bool_prop')
    str_prop = str_property('str_prop')
    index_prop = index_property(0)
    weakref_prop = weakref_property('weakref_prop')
    array_prop = array_property('array_prop')
    lookup_prop = lookup_property('lookup_prop', LOOKUP_DICT)
    func_prop1 = func_property('func_prop1')
    func_prop2 = func_property('func_prop2', FUNC_DICT)

    def __init__(self):
        self.append(12345)


def test_enum_property():
    obj = PropTestClass()

    # Test setter and getter
    obj.enum_prop = 'apple'
    assert obj.enum_prop == 'apple'

    # Test raise
    with pytest.raises(ValueError):
        obj.enum_prop = 'invalid'

    # Test del
    del obj.enum_prop
    assert not hasattr(obj, 'enum_prop')


def test_bool_property():
    obj = PropTestClass()

    # Test setter and getter
    obj.bool_prop = True
    assert obj.bool_prop == True

    obj.bool_prop = False
    assert obj.bool_prop == False

    obj.bool_prop = 'true'
    assert obj.bool_prop == True

    obj.bool_prop = 'false'
    assert obj.bool_prop == False

    # Test raise invalid str
    with pytest.raises(ValueError):
        obj.bool_prop = 'invalid'

    # Test del
    del obj.bool_prop
    assert not hasattr(obj, 'bool_prop')


def test_str_property():
    obj = PropTestClass()
    # Test setter and getter
    obj.str_prop = 1
    assert obj.str_prop == '1'

    # Test del
    del obj.str_prop
    assert not hasattr(obj, 'str_prop')


def test_index_property():
    # Test getter
    obj = PropTestClass()
    assert obj.index_prop == 12345

    # Test setter
    obj.index_prop = 1
    assert tuple(obj) == (1,)


def test_weakref_property():
    obj = PropTestClass()
    other = PropTestClass()

    # Test setter and getter
    obj.weakref_prop = other
    assert obj.weakref_prop == other

    # Test weakref
    del other
    assert obj.weakref_prop is None

    # Test None
    obj.weakref_prop = None
    assert obj.weakref_prop is None

    # Test del
    del obj.weakref_prop
    assert not hasattr(obj, 'weakref_prop')


def test_array_property():
    obj = PropTestClass()

    # Test setter and getter
    obj.array_prop = [1, 2, 3]
    assert pytest.approx(obj.array_prop) == [1, 2, 3]

    # Test del
    del obj.array_prop
    assert not hasattr(obj, 'array_prop')


def test_lookup_property():
    obj = PropTestClass()

    # Test setter and getter
    obj.lookup_prop = 'x'
    assert obj.lookup_prop == 1

    # Test bad value
    with pytest.raises(ValueError):
        obj.lookup_prop = 'bad value'

    # Test del
    del obj.lookup_prop
    assert not hasattr(obj, 'lookup_prop')


def test_func_property():
    # Test setter and getter
    obj = PropTestClass()
    obj.func_prop1 = func
    assert obj.func_prop1 is func

    # Test bad value with no lookup
    with pytest.raises(ValueError):
        obj.func_prop1 = 'bad value'

    # Test setter and getter with lookup
    obj.func_prop2 = 'x'
    assert obj.func_prop2 is func

    # Test bad value with lookup
    with pytest.raises(ValueError):
        obj.func_prop2 = 'bad value'

    # Test del
    del obj.func_prop1
    assert not hasattr(obj, 'func_prop1')

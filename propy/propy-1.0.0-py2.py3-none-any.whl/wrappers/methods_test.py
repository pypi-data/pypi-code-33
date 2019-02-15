from .methods import *


class BaseMethodTest1(object):
    __repr__ = repr_method('x', 'y')

    def __init__(self):
        self.x, self.y, self.z = 1, 2, 3


class BaseMethodTest2(object):
    __repr__ = repr_method('__all__')

    def __init__(self):
        self.x, self.y, self.z = 1, 2, 3


def test_repr_method():
    # Test specified
    a = BaseMethodTest1()
    assert repr(a) == 'BaseMethodTest1(x=1, y=2)'

    a = BaseMethodTest2()
    assert repr(a) == 'BaseMethodTest2(x=1, y=2, z=3)'

"""
A module to recursively compare any object considering the types of all their constituents
and using two strategies to perform almost equality checks of floats.
"""

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

import unittest
from collections import namedtuple, OrderedDict
from dataclasses import dataclass
from typing import Any, cast, Dict


def are_almost_equal(  # pylint: disable=R0911,R0912
        obj1: Any,
        obj2: Any,
        max_abs_ratio_diff: float,
        max_abs_diff: float
) -> bool:
    """
    Compares two objects by recursively walking them trough. Equality is as usual except for floats.
    Floats are compared according to the two measures defined below.

    :param obj1: The first object.
    :param obj2: The second object.
    :param max_abs_ratio_diff: The maximum allowed absolute value of the difference.
    `abs(1 - (obj1 / obj2)` and vice-versa if obj2 == 0.0. Ignored if < 0.
    :param max_abs_diff: The maximum allowed absolute difference `abs(obj1 - obj2)`. Ignored if < 0.
    :return: Whether the two objects are almost equal.
    """
    if type(obj1) is not type(obj2):
        return False

    composite_type_passed = False

    if hasattr(obj1, '__slots__'):
        if len(obj1.__slots__) != len(obj2.__slots__):
            return False
        if any(not are_almost_equal(getattr(obj1, s1), getattr(obj2, s2),
                                    max_abs_ratio_diff, max_abs_diff)
               for s1, s2 in zip(sorted(obj1.__slots__), sorted(obj2.__slots__))):
            return False

        composite_type_passed = True

    if hasattr(obj1, '__dict__'):
        if len(obj1.__dict__) != len(obj2.__dict__):
            return False
        if any(not are_almost_equal(k1, k2, max_abs_ratio_diff, max_abs_diff)
               or not are_almost_equal(v1, v2, max_abs_ratio_diff, max_abs_diff)
               for ((k1, v1), (k2, v2))
               in zip(sorted(obj1.__dict__.items()), sorted(obj2.__dict__.items()))
               if not k1.startswith('__')):  # avoid infinite loops
            return False

        composite_type_passed = True

    if isinstance(obj1, dict):
        if len(obj1) != len(obj2):
            return False
        if any(not are_almost_equal(k1, k2, max_abs_ratio_diff, max_abs_diff)
               or not are_almost_equal(v1, v2, max_abs_ratio_diff, max_abs_diff)
               for ((k1, v1), (k2, v2)) in zip(sorted(obj1.items()), sorted(obj2.items()))):
            return False

    elif any(issubclass(obj1.__class__, c) for c in (list, tuple, set)):
        if len(obj1) != len(obj2):
            return False
        if any(not are_almost_equal(v1, v2, max_abs_ratio_diff, max_abs_diff)
               for v1, v2 in zip(obj1, obj2)):
            return False

    elif isinstance(obj1, float):
        if obj1 == obj2:
            return True

        if max_abs_ratio_diff > 0:  # if max_abs_ratio_diff < 0, max_abs_ratio_diff is ignored
            if obj2 != 0:
                if abs(1.0 - (obj1 / obj2)) > max_abs_ratio_diff:
                    return False
            else:  # if both == 0, we already returned True
                if abs(1.0 - (obj2 / obj1)) > max_abs_ratio_diff:
                    return False
        if 0 < max_abs_diff < abs(obj1 - obj2):  # if max_abs_diff < 0, max_abs_diff is ignored
            return False
        return True

    else:
        if not composite_type_passed:
            return cast(bool, obj1 == obj2)

    return True


class EqualityTest(unittest.TestCase):
    """
    Test cases for are_almost_equal
    """

    def test_floats(self) -> None:
        """
        Test float comparison strategies
        """
        obj1 = ('hi', 3, 3.4)
        obj2 = ('hi', 3, 3.400001)
        self.assertTrue(are_almost_equal(obj1, obj2, 0.0001, 0.0001))
        self.assertFalse(are_almost_equal(obj1, obj2, 0.00000001, 0.00000001))

    def test_ratio_only(self) -> None:
        """
        Tests ratio comparison strategy only
        """
        obj1 = ['hey', 10000, 123.12]
        obj2 = ['hey', 10000, 123.80]
        self.assertTrue(are_almost_equal(obj1, obj2, 0.01, -1))
        self.assertFalse(are_almost_equal(obj1, obj2, 0.001, -1))

    def test_diff_only(self) -> None:
        """
        Tests diff comparison strategy only
        """
        obj1 = ['hey', 10000, 1234567890.12]
        obj2 = ['hey', 10000, 1234567890.80]
        self.assertTrue(are_almost_equal(obj1, obj2, -1, 1))
        self.assertFalse(are_almost_equal(obj1, obj2, -1, 0.1))

    def test_both_ignored(self) -> None:
        """
        Tests that both strategies are ignored
        """
        obj1 = ['hey', 10000, 1234567890.12]
        obj2 = ['hey', 10000, 0.80]
        obj3 = ['hi', 10000, 0.80]
        self.assertTrue(are_almost_equal(obj1, obj2, -1, -1))
        self.assertFalse(are_almost_equal(obj1, obj3, -1, -1))

    def test_different_lengths(self) -> None:
        """
        Tests that returns false if containers have different lengths
        """
        obj1 = ['hey', 1234567890.12, 10000]
        obj2 = ['hey', 1234567890.80]
        self.assertFalse(are_almost_equal(obj1, obj2, 1, 1))

    def test_classes(self) -> None:
        """
        Test comparing function using class arguments.
        Monkey patched classes should also be supported.
        """

        # pylint: disable=C0111,C0103,R0903
        class A:
            d = 12.3

            def __init__(self, a: float, b: str, c: Dict[Any, Any]) -> None:
                self.attr_a = a
                self.attr_b = b
                self.attr_c = c

        obj1: A = A(2.34, 'str', {1: 'hey', 345.23: [123, 'hi', 890.12]})
        obj2: A = A(2.34, 'str', {1: 'hey', 345.231: [123, 'hi', 890.121]})
        self.assertTrue(are_almost_equal(obj1, obj2, 0.1, 0.1))
        self.assertFalse(are_almost_equal(obj1, obj2, 0.0001, 0.0001))

        # This should fail even if no float inequality is considered because we add a new attribute
        # pylint: disable=W0201
        obj2.hello = 'hello'  # type: ignore
        self.assertFalse(are_almost_equal(obj1, obj2, -1, -1))

    def test_namedtuples(self) -> None:
        """
        Test support for namedtuples
        """
        B = namedtuple('B', ['x', 'y'])
        obj1 = B(3.3, 4.4)
        obj2 = B(3.4, 4.5)
        self.assertTrue(are_almost_equal(obj1, obj2, 0.2, 0.2))
        self.assertFalse(are_almost_equal(obj1, obj2, 0.001, 0.001))

    def test_classes_with_slots(self) -> None:
        """
        Tests support for classes with no __dict__, that use __slots__
        """

        # pylint: disable=C0111,C0103,R0903
        class C:
            __slots__ = ['attr_a', 'attr_b']

            def __init__(self, a: float, b: float) -> None:
                self.attr_a = a
                self.attr_b = b

        obj1: C = C(3.3, 4.4)
        obj2: C = C(3.4, 4.5)
        self.assertTrue(are_almost_equal(obj1, obj2, 0.3, 0.3))
        self.assertFalse(are_almost_equal(obj1, obj2, -1, 0.01))

    def test_dataclasses(self) -> None:
        """
        Tests support for dataclasses
        """

        # pylint: disable=C0111,C0103
        @dataclass
        class D:
            s: str
            i: int
            f: float

        # pylint: disable=C0111,C0103
        @dataclass
        class E:
            f2: float
            f4: str
            d: D

        obj1 = E(12.3, 'hi', D('hello', 34, 20.01))
        obj2 = E(12.1, 'hi', D('hello', 34, 20.0))
        self.assertTrue(are_almost_equal(obj1, obj2, -1, 0.4))
        self.assertFalse(are_almost_equal(obj1, obj2, -1, 0.001))

        obj3 = E(12.1, 'hi', D('ciao', 34, 20.0))
        self.assertFalse(are_almost_equal(obj2, obj3, -1, -1))

    def test_ordereddict(self) -> None:
        """
        Tests support for OrderedDict
        """
        obj1 = OrderedDict({1: 'hey', 345.23: [123, 'hi', 890.12]})
        obj2 = OrderedDict({1: 'hey', 345.23: [123, 'hi', 890.0]})
        self.assertTrue(are_almost_equal(obj1, obj2, 0.01, -1))
        self.assertFalse(are_almost_equal(obj1, obj2, 0.0001, -1))

import unittest

from parameterized import parameterized

from anji_orm import Interval


class IntervalTest(unittest.TestCase):

    @parameterized.expand([
        (5, Interval(4, 6)),
        (5, Interval(4, 5, right_close=True)),
        (5, Interval(5, 6, left_close=True))
    ])
    def test_interval_contains(self, value, interval):
        self.assertTrue(value in interval)

    @parameterized.expand([
        (5, Interval(4, 5)),
        (5, Interval(7, 8))
    ])
    def test_interval_not_contains(self, value, interval):
        self.assertFalse(value in interval)

    @parameterized.expand([
        (Interval(3, 7), Interval(4, 6)),
        (Interval(4, 7), Interval(4, 6)),
        (Interval(3, 6), Interval(4, 6)),
        (Interval(4, 7, left_close=True), Interval(4, 6)),
        (Interval(4, 7, right_close=True), Interval(5, 7))
    ])
    def test_internal_contains_interval(self, first, second):
        self.assertTrue(first.contains_interval(second))

    @parameterized.expand([
        (Interval(4, 6), Interval(3, 7)),
        (Interval(4, 6), Interval(4, 7)),
        (Interval(4, 6), Interval(3, 6)),
        (Interval(4, 7), Interval(5, 7, right_close=True)),
        (Interval(4, 7), Interval(4, 6, left_close=True))
    ])
    def test_internal_not_contains(self, first, second):
        self.assertFalse(first.contains_interval(second))

    @parameterized.expand([
        (Interval(3, 5), '5'),
        (Interval(3, 5), 5),
        (Interval(3, 5), object()),
    ])
    def test_internal_with_not_interval(self, interval, value):
        self.assertNotEqual(interval, value)

    @parameterized.expand([
        (Interval(3, 5), '(3, 5)'),
        (Interval(3, 5, left_close=True), '[3, 5)'),
        (Interval(3, 5, right_close=True), '(3, 5]'),
        (Interval(3, 5, left_close=True, right_close=True), '[3, 5]')
    ])
    def test_convertation_to_string(self, interval, result):
        self.assertEqual(str(interval), result)

    @parameterized.expand([
        (Interval(3, 5),),
        (Interval(3, 5, left_close=True),),
        (Interval(3, 5, right_close=True),),
        (Interval(3, 5, left_close=True, right_close=True),),
        (Interval(3, 3, left_close=True, right_close=True),)
    ])
    def test_is_valid(self, interval):
        self.assertTrue(interval.valid)

    @parameterized.expand([
        (Interval(3, 3, left_close=True),),
        (Interval(3, 3, right_close=True),),
        (Interval(3, 3),),
        (Interval(5, 3),)
    ])
    def test_is_not_valid(self, interval):
        self.assertFalse(interval.valid)

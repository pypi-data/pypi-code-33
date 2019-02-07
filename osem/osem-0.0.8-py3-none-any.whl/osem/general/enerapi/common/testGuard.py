import unittest

from common.DomainException import DomainException

from osem.general.enerapi.common.Guard import *


class TestCheckExist(unittest.TestCase):
    def test_1(self):
        Guard.check_if_key_in_dict("foo", {"foo": 0})

    def test_2(self):
        with self.assertRaises(DomainException):
            Guard.check_if_key_in_dict("bar", {"foo": 0})


class TestCheckInList(unittest.TestCase):
    def test_1(self):
        Guard.check_if_value_in_list("foo", values=["foo"])

    def test_2(self):
        with self.assertRaises(DomainException):
            Guard.check_if_value_in_list("bar", values=["foo"])


class TestCheckBetween(unittest.TestCase):
    def test_1(self):
        Guard.check_value_in_between(1, min=0, max=1)

    def test_2(self):
        with self.assertRaises(DomainException):
            Guard.check_value_in_between(1, min=0, max=1, max_in=False)

    def test_3(self):
        Guard.check_value_in_between(0, min=0, max=1)

    def test_4(self):
        with self.assertRaises(DomainException):
            Guard.check_value_in_between(0, min=0, max=1, min_in=False)

    def test_5(self):
        Guard.check_value_in_between(1, min=0, max=1, min_in=False)

    def test_6(self):
        Guard.check_value_in_between(0, min=0, max=1, max_in=False)

    def test_7(self):
        with self.assertRaises(DomainException):
            Guard.check_value_in_between(0, min=0, max=1, min_in=False, max_in=False)

    def test_8(self):
        with self.assertRaises(DomainException):
            Guard.check_value_in_between(1, min=0, max=1, max_in=False, min_in=False)

    def test_9(self):
        Guard.check_value_in_between(1, min=1, max=1, max_in=True)

    def test_10(self):
        Guard.check_value_in_between(0, min=0, max=0, min_in=True)

    def test_11(self):
        with self.assertRaises(DomainException):
            Guard.check_value_in_between(1, min=1, max=0)

    def test_12(self):
        with self.assertRaises(DomainException):
            Guard.check_value_in_between(1, min=0)

    def test_13(self):
        with self.assertRaises(DomainException):
            Guard.check_value_in_between(1, max=0)


class TestCheckIsHigher(unittest.TestCase):

    def test_1(self):
        with self.assertRaises(DomainException):
            Guard.check_is_higher(0, lower_limit=0, strict=True)

    def test_2(self):
        Guard.check_is_higher(0, lower_limit=0, strict=False)

    def test_3(self):
        Guard.check_is_higher(1, lower_limit=0, strict=True)

    def test_4(self):
        with self.assertRaises(DomainException):
            Guard.check_is_higher(0, lower_limit=1, strict=False)

    def test_5(self):
        with self.assertRaises(DomainException):
            Guard.check_is_higher(0, lower_limit=1)

    def test_6(self):
        Guard.check_is_higher(0, lower_limit=0)


class TestCheckListLengths(unittest.TestCase):
    def test_1(self):
        Guard.check_for_same_list_lengths(l1=[1, 2, 3], l2=[1, 2, 3])

    def test_2(self):
        with self.assertRaises(DomainException):
            Guard.check_for_same_list_lengths(l1=[1, 2, 3], l2=[1, 2])


class TestCheckForEveryItemOfList(unittest.TestCase):
    def test_1(self):
        Guard.check_for_every_item_of_list([1, 2, 3], Guard.check_is_higher, lower_limit=0)

    def test_2(self):
        Guard.check_for_every_item_of_list([1, 2, 3], Guard.check_is_higher, lower_limit=0, strict=True)

    def test_3(self):
        with self.assertRaises(DomainException):
            Guard.check_for_every_item_of_list([1, 2, 3], Guard.check_is_higher, lower_limit=2)


class TestCheckForMinimumNumberOfValueInAList(unittest.TestCase):
    def test_1(self):
        Guard.check_for_minimum_number_of_value_in_a_list([1, 2, 3], min=3)

    def test_2(self):
        with self.assertRaises(DomainException):
            Guard.check_for_minimum_number_of_value_in_a_list([1, 2, 3], min=4)


class TestCheckForSortedList(unittest.TestCase):
    def test_1(self):
        Guard.check_if_list_is_sorted([1, 2, 3])

    def test_2(self):
        Guard.check_if_list_is_sorted([3, 2, 1], reverse=True)

    def test_3(self):
        with self.assertRaises(DomainException):
            Guard.check_if_list_is_sorted([1, 3, 2])

    def test_4(self):
        with self.assertRaises(DomainException):
            Guard.check_if_list_is_sorted([3, 2, 1])

    def test_5(self):
        with self.assertRaises(DomainException):
            Guard.check_if_list_is_sorted([1, 2, 3], reverse=True)

    def test_6(self):
        with self.assertRaises(DomainException):
            Guard.check_if_list_is_sorted([3, 2, 1], reverse=False)

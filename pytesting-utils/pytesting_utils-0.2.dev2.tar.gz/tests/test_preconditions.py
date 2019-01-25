# -*- coding: utf-8 -*-
import unittest

from pytesting_utils.preconditions import (
    Preconditions,
    NoneValueException,
    IllegalStateException,
    IllegalArgumentException,
)


class PreconditionsTest(unittest.TestCase):
    def test_check_not_none_without_none_no_msg(self):
        i = 42
        self.assertEqual(i, Preconditions.check_not_none(i))

    def test_check_not_none_without_none_msg(self):
        i = 42
        r = Preconditions.check_not_none(i, "message")
        self.assertEqual(i, r)

    def test_check_not_none_with_none_no_msg(self):
        i = None
        with self.assertRaises(NoneValueException) as context:
            Preconditions.check_not_none(i)
        self.assertTrue(isinstance(context.exception, NoneValueException))

    def test_check_not_none_with_none_msg(self):
        i = None
        m = "message"
        with self.assertRaises(NoneValueException) as context:
            Preconditions.check_not_none(i, m)
        self.assertTrue(m in str(context.exception))

    def test_check_state_true_no_msg(self):
        try:
            Preconditions.check_state(True)
        except IllegalStateException:  # pragma: no cover
            self.fail(
                "check_state() raised IllegalStateException " "unexpectedly!"
            )  # pragma: no cover

    def test_check_state_true_msg(self):
        try:
            Preconditions.check_state(True, "message")
        except IllegalStateException:  # pragma: no cover
            self.fail(
                "check_state() raised IllegalStateException " "unexpectedly!"
            )  # pragma: no cover

    def test_check_state_false_no_msg(self):
        with self.assertRaises(IllegalStateException) as context:
            Preconditions.check_state(False)
        self.assertTrue(isinstance(context.exception, IllegalStateException))

    def test_check_state_false_msg(self):
        m = "message"
        with self.assertRaises(IllegalStateException) as context:
            Preconditions.check_state(False, m)
        self.assertTrue(m in str(context.exception))

    def test_check_argument_true_no_msg(self):
        try:
            Preconditions.check_argument(True)
        except IllegalArgumentException:  # pragma: no cover
            self.fail(
                "check_argument() raised IllegalArgumentException "
                "unexpectedly!"
            )  # pragma: no cover

    def test_check_argument_true_msg(self):
        try:
            Preconditions.check_argument(True, "message")
        except IllegalArgumentException:  # pragma: no cover
            self.fail(
                "check_argument() raised IllegalArgumentException "
                "unexpectedly!"
            )  # pragma: no cover

    def test_check_argument_false_no_msg(self):
        with self.assertRaises(IllegalArgumentException) as context:
            Preconditions.check_argument(False)
        self.assertTrue(isinstance(context.exception, IllegalArgumentException))

    def test_check_argument_false_msg(self):
        m = "message"
        with self.assertRaises(IllegalArgumentException) as context:
            Preconditions.check_argument(False, m)
        self.assertTrue(m in str(context.exception))


if __name__ == "__main__":
    unittest.main()

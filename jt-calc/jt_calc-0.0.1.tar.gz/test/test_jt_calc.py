from unittest import TestCase

import jt_calc


class TestJTCalc(TestCase):

    def test_add(self):
        expected = 10
        num1 = 5
        num2 = 5
        actual = jt_calc.add(num1, num2)
        self.assertEqual(expected, actual)

    def test_subtract(self):
        expected = 10
        num1 = 15
        num2 = 5
        actual = jt_calc.subtract(num1, num2)
        self.assertEqual(expected, actual)

    def test_multiply(self):
        expected = 25
        num1 = 5
        num2 = 5
        actual = jt_calc.multiply(num1, num2)
        self.assertEqual(expected, actual)

    def test_divide(self):
        expected = 3
        num1 = 15
        num2 = 5
        actual = jt_calc.divide(num1, num2)
        self.assertEqual(expected, actual)

    def test_divide_0(self):
        expected = "You're a fool"
        num1 = 5
        num2 = 0
        actual = jt_calc.divide(num1, num2)
        self.assertEqual(expected, actual)


# That's all folks...

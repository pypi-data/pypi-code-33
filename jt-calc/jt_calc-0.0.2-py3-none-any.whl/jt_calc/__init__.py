"""
jt_calc Python package is a simple custom calculator in Python 3.7.
By Joe Tilsed
---
Here is where the operations are
"""

name = "jt_calc"


def add(num1, num2):
    """
    Adding two numbers together
    :param num1:
    The first number
    :param num2:
    The second number
    :return:
    The result of adding num1 to num2
    """
    return num1 + num2


def subtract(num1, num2):
    """
    Subtracting num2 from num1
    :param num1:
    The original number
    :param num2:
    The number to be subtracted from num1
    :return:
    The result of subtracting num2 from num1
    """
    return num1 - num2


def multiply(num1, num2):
    """
    Multiply the two given numbers together
    :param num1:
    The first number
    :param num2:
    The second number
    :return:
    The result of multiplying num1 to num2
    """
    return num1 * num2


def divide(num1, num2):
    """
    Divide num1 by num2
    :param num1:
    The original number
    :param num2:
    The number the original number needs to be divided into
    :return:
    The result of dividing num1 by num2
    """
    if num2 == 0:
        return "You're a fool"
    return num1 / num2


def power_of(num1, num2):
    """
    num1 to the power of num2
    :param num1:
    The original number
    :param num2:
    The number of times the original number is to be timed by itself
    :return:
    The result of num1 to the power of num2
    """
    return num1 ** num2


# That's all folks...

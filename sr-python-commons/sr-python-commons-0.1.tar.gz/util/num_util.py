import math
import re


NUMERIC_CONST_PATTERN = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
REGEX_NUM = re.compile(NUMERIC_CONST_PATTERN, re.VERBOSE)


def extract_num(a_str: str, num_type=None):
    num = REGEX_NUM.findall(a_str)
    num_text = num[0][:-1] if num[0].endswith('.') else num[0]
    return num_type(num_text) if num_type else num_text


def extract_nums(a_str: str, num_type=None):
    nums = REGEX_NUM.findall(a_str)
    if num_type:
        return map(lambda x: num_type(x), nums)
    else:
        return nums


def trunc_float(num, precision):
    return '%.*f' % (precision, num)


def trunc(f, n):
    """Truncates/pads a float f to n decimal places without rounding"""
    return math.floor(f * 10 ** n) / 10 ** n

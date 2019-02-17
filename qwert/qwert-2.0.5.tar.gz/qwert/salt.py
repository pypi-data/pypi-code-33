#!/usr/bin/env python
# encoding: utf-8

import random


def salt(length: int = None,
         with_hint: bool = False,
         seed: str = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
         ):
    """
    Salt generator.

    :param int length: Length
    :param bool with_hint: Whether need a hint
    :param str seed: Seed
    :return: tuple or str
    """
    length = length or random.randint(8, 12)

    s = []
    for i in range(length):
        s.append(random.choice(seed))
    r = ''.join(s)

    if with_hint:
        return r, shrink_to_hint(r)
    else:
        return r


def shrink_to_hint(s: str):
    """
    Shrink a string to hint.

    :param str s: Source string
    :return: str
    """
    length = len(s)
    if length < 4:
        return '*' * length

    return '{}**{}'.format(s[0], s[length - 1])

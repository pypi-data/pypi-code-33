#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time   : 2018/12/21 2:52 PM 
# @Author : xbzheng

"""
Test Counter
"""

import unittest
from kafkatool.metrics.counter import Counter


class TestCounter(unittest.TestCase):

    def test_incr(self):
        c = Counter()
        c.incr('a')
        c.incr('b')
        c.incr('b')
        self.assertDictEqual({'a': 1, 'b': 2}, c)

    def test_decr(self):
        c = Counter()
        c.incr('b', 4)
        c.decr('b', 1)
        self.assertDictEqual({'b': 3}, c)

    def test_reset(self):
        c = Counter()
        c.incr('a', 4)
        c.incr('b', 1)
        c.reset()
        self.assertDictEqual({'a': 0, 'b': 0}, c)


if __name__ == '__main__':
    unittest.main()

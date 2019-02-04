# -*- coding: utf-8 -*-

from .context import metrics

import unittest


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')


if __name__ == '__main__':
    unittest.main()
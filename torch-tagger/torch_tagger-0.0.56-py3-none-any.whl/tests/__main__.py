# -*- coding: utf-8 -*-
"""Test Entry"""

import unittest

if __name__ == '__main__':
    testsuite = unittest.TestLoader().discover('.', pattern='test*.py')
    unittest.TextTestRunner(verbosity=1).run(testsuite)

import unittest
from .core import *
import os

sep = os.path.sep

class Test(unittest.TestCase):
    def test_join(self):
        s = Path('')
        self.assertEqual(s.join('a'), 'a')
        self.assertEqual(s.join('a', '.'), 'a')
        self.assertEqual(s.join('a/b'), 'a' + sep + 'b')
        self.assertEqual(s.join('a/b', '..'), 'a')
        self.assertEqual(s.join('a\\b', '..'), 'a')
        self.assertEqual(s.join('a/b').join('..'), 'a')
        self.assertEqual(s.join('..'), '..')
        self.assertEqual(s.join('a').join('..'), '.')


if __name__ == '__main__':
    unittest.main()

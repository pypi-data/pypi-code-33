import unittest
from ybc_todo import *


class MyTestCase(unittest.TestCase):
    def test_todo(self):
        self.assertNotEqual(-1, todo())


if __name__ == '__main__':
    unittest.main()

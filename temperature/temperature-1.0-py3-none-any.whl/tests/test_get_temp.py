import unittest
from temperature import temp


class MyTestCase(unittest.TestCase):
    def test_get_temp(self):
        self.assertEqual(temp.value, -1)


if __name__ == '__main__':
    unittest.main()

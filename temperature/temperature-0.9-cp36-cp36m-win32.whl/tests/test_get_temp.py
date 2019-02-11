import unittest


class MyTestCase(unittest.TestCase):
    def test_get_temp(self):
        from temperature import get_temp
        current_temp = get_temp()
        self.assertEqual(current_temp, -1)


if __name__ == '__main__':
    unittest.main()

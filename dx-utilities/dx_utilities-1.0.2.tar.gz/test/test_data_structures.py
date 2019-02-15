import unittest

from dx_utilities.data_structures import TolerantDict


class TestTolerantDict(unittest.TestCase):

    def test_int_tolerance(self):
        a = TolerantDict({k: 0 for k in range(10)})
        self.assertEqual(a["0"], 0)
        self.assertEqual(a[0.], 0)
        with self.assertRaises(ValueError):
            a["asdf"]

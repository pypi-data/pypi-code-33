# coding: utf-8
import unittest
from tma.plate import Plate
from tma.collector import ts


class TestPlate(unittest.TestCase):
    def setUp(self):
        name = '5G'
        concepts = ts.get_share_concepts()
        shares = list(concepts[concepts['concept'] == name]['ts_code'])
        self.plate = Plate(name, shares, cache_interval=0)

    def test_len(self):
        self.assertTrue(len(self.plate) > 0)


if __name__ == '__main__':
    unittest.main()

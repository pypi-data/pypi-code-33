# import sys
# sys.path.append('..')
from grouplabelencode import grouplabelencode

import unittest
import numpy.testing as npt


class Test_GrouplabelencodeFunc(unittest.TestCase):

    def test1(self):
        grp = [['a', 'b', 'c'], ['d', 'e']]
        data = ['a', 'b', 'c', 'c', 'b', 'b', 'e', 'z', 'd', 'a']
        target = [0, 0, 0, 0, 0, 0, 1, 2, 1, 0]
        npt.assert_allclose(grouplabelencode(data, grp, nastate=True), target)

    def test2(self):
        grp = {0: ['a', 'b', 'c'], 1: ['d', 'e']}
        data = ['a', 'b', 'c', 'c', 'b', 'b', 'e', 'z', 'd', 'a']
        target = [0, 0, 0, 0, 0, 0, 1, 2, 1, 0]
        npt.assert_allclose(grouplabelencode(data, grp, nastate=True), target)


# run
if __name__ == '__main__':
    unittest.main()

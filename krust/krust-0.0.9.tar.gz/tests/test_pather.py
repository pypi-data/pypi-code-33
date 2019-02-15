# -*- coding:utf-8 -*-

import six
import os
import sys
import unittest
from krust.file_utils import *
from krust.pather import *


class TestPather(unittest.TestCase):
    def setUp(self):
        self.pather = Pather(paths=[os.path.join('pather_paths', abc) for abc in 'ABC'])

    def tearDown(self):
        pass

    def test_cascading(self):
        self.assertEqual(self.pather['item1'], 'pather_paths/C/item1')
        self.assertEqual(self.pather['item2'], 'pather_paths/B/item2')

    @unittest.skipIf(sys.platform.startswith("win"), "Non-windows only")
    def test_sys_confs(self):
        conf_pather = Pather(paths=['/etc', os.path.join('pather_paths', 'A')])
        self.assertEqual(conf_pather['profile'], 'pather_paths/A/profile')
        self.assertEqual(conf_pather['hosts'], '/etc/hosts')


if __name__ == '__main__':
    unittest.main()
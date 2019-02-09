# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import upt

from upt_nix.upt_nix import NixPythonPackage


class TestNixPythonPackage(unittest.TestCase):
    def setUp(self):
        self.upt_pkg = upt.Package('foo', '1.0')
        self.nix_pkg = NixPythonPackage(self.upt_pkg)

    def test_to_nix_name(self):
        self.assertEqual(self.nix_pkg._to_nix_name('Jinja2'), 'jinja2')


if __name__ == '__main__':
    unittest.main()

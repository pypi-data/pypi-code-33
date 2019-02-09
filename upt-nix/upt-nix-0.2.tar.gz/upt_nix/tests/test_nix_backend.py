# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import upt

from upt_nix.upt_nix import NixBackend


class TestNixBackend(unittest.TestCase):
    def setUp(self):
        self.backend = NixBackend()

    def test_unhandled_frontend(self):
        upt_pkg = upt.Package('foo', '42')
        upt_pkg.frontend = 'invalid frontend'
        with self.assertRaises(upt.UnhandledFrontendError):
            self.backend.create_package(upt_pkg)

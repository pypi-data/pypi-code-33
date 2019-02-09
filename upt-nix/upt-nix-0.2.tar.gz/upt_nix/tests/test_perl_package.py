# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import upt

from upt_nix.upt_nix import NixPerlPackage


class TestNixPerlPackage(unittest.TestCase):
    def setUp(self):
        self.upt_pkg = upt.Package('foo', '1.0')
        self.nix_pkg = NixPerlPackage(self.upt_pkg)

    def test_to_nix_name(self):
        self.assertEqual(self.nix_pkg._to_nix_name('Test::More'), 'TestMore')

    def test_url(self):
        self.upt_pkg.archives = [
            upt.Archive('http://www.example.com/source.tar.gz',
                        sha256='sha256')
        ]
        self.assertEqual(self.nix_pkg.url,
                         'http://www.example.com/source.tar.gz')

    def test_urlformat(self):
        url = "https://cpan.metacpan.org/"
        url += "authors/id/T/TI/TINITA/YAML-1.27.tar.gz"
        expected = "mirror://cpan/authors/id/T/TI/TINITA/YAML-1.27.tar.gz"
        self.assertEqual(self.nix_pkg.urlformat(url), expected)


if __name__ == '__main__':
    unittest.main()

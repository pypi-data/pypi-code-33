# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import upt

from upt_nix.upt_nix import NixPackage


class TestNixPackage(unittest.TestCase):
    def setUp(self):
        self.upt_pkg = upt.Package('foo', '1.0')
        self.nix_pkg = NixPackage(self.upt_pkg)

    def test_getattribute(self):
        self.assertEqual(self.nix_pkg.name, self.upt_pkg.name)
        self.assertEqual(self.nix_pkg.version, self.upt_pkg.version)
        self.upt_pkg.homepage = 'http://foo.com'
        self.assertEqual(self.nix_pkg.homepage, self.upt_pkg.homepage)
        self.upt_pkg.summary = 'summary'
        self.assertEqual(self.nix_pkg.summary, self.upt_pkg.summary)

    def test_licenses(self):
        self.upt_pkg.licenses = []
        self.assertListEqual(self.nix_pkg.licenses, [])

        self.upt_pkg.licenses = [upt.licenses.BSDThreeClauseLicense()]
        self.assertListEqual(self.nix_pkg.licenses, ['licenses.bsd3'])

        self.upt_pkg.licenses = [
            upt.licenses.BSDTwoClauseLicense(),
            upt.licenses.BSDThreeClauseLicense(),
        ]
        self.assertListEqual(self.nix_pkg.licenses,
                             ['licenses.bsd2', 'licenses.bsd3'])

    def test_native_build_inputs(self):
        self.upt_pkg.requirements = {
            'build': [upt.PackageRequirement('pkg1', '')]
        }
        self.assertListEqual(self.nix_pkg.native_build_inputs, ['pkg1'])

        self.upt_pkg.requirements = {
            'test': [upt.PackageRequirement('pkg2', '')]
        }
        self.assertListEqual(self.nix_pkg.native_build_inputs, ['pkg2'])

        self.upt_pkg.requirements = {
            'build': [upt.PackageRequirement('pkg1', '')],
            'test': [upt.PackageRequirement('pkg2', '')]
        }
        self.assertListEqual(self.nix_pkg.native_build_inputs,
                             ['pkg2', 'pkg1'])

    def test_propagated_build_inputs(self):
        self.upt_pkg.requirements = {
            'run': []
        }
        self.assertListEqual(self.nix_pkg.propagated_build_inputs, [])

        self.upt_pkg.requirements = {
            'run': [upt.PackageRequirement('pkg1', '')]
        }
        self.assertListEqual(self.nix_pkg.propagated_build_inputs, ['pkg1'])

    def test_urlformat(self):
        url = 'http://www.example.com/source.tar.gz'
        self.assertEqual(self.nix_pkg.urlformat(url), url)

    def test_url(self):
        url = 'http://www.example.com/source.tar.gz'
        self.upt_pkg.archives = [
            upt.Archive(url, sha256='sha256')
        ]
        self.assertEqual(self.nix_pkg.url, url)

    def test_url_no_archive(self):
        self.upt_pkg.archives = []
        self.assertEqual(self.nix_pkg.url, 'TODO')

    def test_get_sha256(self):
        self.upt_pkg.archives = [
            upt.Archive('http://www.example.com/source.tar.gz',
                        sha256='sha256')
        ]
        self.assertEqual(self.nix_pkg.sha256, 'sha256')

    def test_get_sha256_no_archives(self):
        self.archives = []
        self.assertEqual(self.nix_pkg.sha256, 'TODO')


if __name__ == '__main__':
    unittest.main()

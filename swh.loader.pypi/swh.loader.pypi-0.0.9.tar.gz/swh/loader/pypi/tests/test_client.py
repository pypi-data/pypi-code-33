# Copyright (C) 2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os

from swh.loader.pypi import converters
from swh.loader.pypi.client import _project_pkginfo

from .common import WithProjectTest


class PyPIProjectTest(WithProjectTest):
    def test_download_new_releases(self):
        actual_releases = self.project.download_new_releases([])

        expected_release_artifacts = {
            '1.1.0': {
                'archive_type': 'zip',
                'blake2s256': 'df9413bde66e6133b10cadefad6fcf9cbbc369b47831089112c846d79f14985a',  # noqa
                'date': '2016-01-31T05:28:42',
                'filename': '0805nexter-1.1.0.zip',
                'sha1': '127d8697db916ba1c67084052196a83319a25000',
                'sha1_git': '4b8f1350e6d9fa00256e974ae24c09543d85b196',
                'sha256': '52cd128ad3afe539478abc7440d4b043384295fbe6b0958a237cb6d926465035',  # noqa
                'size': 862,
                'url': 'https://files.pythonhosted.org/packages/ec/65/c0116953c9a3f47de89e71964d6c7b0c783b01f29fa3390584dbf3046b4d/0805nexter-1.1.0.zip',  # noqa
            },
            '1.2.0': {
                'archive_type': 'zip',
                'blake2s256': '67010586b5b9a4aaa3b1c386f9dc8b4c99e6e40f37732a717a5f9b9b1185e588', # noqa
                'date': '2016-01-31T05:51:25',
                'filename': '0805nexter-1.2.0.zip',
                'sha1': 'd55238554b94da7c5bf4a349ece0fe3b2b19f79c',
                'sha1_git': '8638d33a96cb25d8319af21417f00045ec6ee810',
                'sha256': '49785c6ae39ea511b3c253d7621c0b1b6228be2f965aca8a491e6b84126d0709',  # noqa
                'size': 898,
                'url': 'https://files.pythonhosted.org/packages/c4/a0/4562cda161dc4ecbbe9e2a11eb365400c0461845c5be70d73869786809c4/0805nexter-1.2.0.zip',  # noqa
            }
        }

        expected_releases = {
            '1.1.0': {
                'name': '1.1.0',
                'message': '',
            },
            '1.2.0': {
                'name': '1.2.0',
                'message': '',
            },
        }

        dir_paths = []
        for pkginfo, author, release, artifact, dir_path in actual_releases:
            version = pkginfo['version']
            expected_pkginfo = _project_pkginfo(dir_path)
            self.assertEqual(pkginfo, expected_pkginfo)
            expected_author = converters.author(expected_pkginfo)
            self.assertEqual(author, expected_author)
            expected_artifact = expected_release_artifacts[version]
            self.assertEqual(artifact, expected_artifact)
            expected_release = expected_releases[version]
            self.assertEqual(release, expected_release)

            self.assertTrue(version in dir_path)
            self.assertTrue(self.project_name in dir_path)
            # path still exists
            self.assertTrue(os.path.exists(dir_path))
            dir_paths.append(dir_path)

        # Ensure uncompressed paths have been destroyed
        for dir_path in dir_paths:
            # path no longer exists
            self.assertFalse(os.path.exists(dir_path))

    def test_all_release_artifacts(self):
        expected_release_artifacts = {
            '1.1.0': [(
                '0805nexter-1.1.0.zip',
                '52cd128ad3afe539478abc7440d4b043'
                '384295fbe6b0958a237cb6d926465035',
            )],
            '1.2.0': [(
                '0805nexter-1.2.0.zip',
                '49785c6ae39ea511b3c253d7621c0b1b'
                '6228be2f965aca8a491e6b84126d0709',
            )],
        }

        self.assertEqual(
            self.project.all_release_artifacts(),
            expected_release_artifacts,
        )

    def test_default_release(self):
        self.assertEqual(self.project.default_release(), '1.2.0')

# Copyright (C) 2016-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import json
import tempfile

import pytest

from swh.loader.core.tests import BaseLoaderTest
from swh.loader.pypi.client import PyPIProject
from swh.loader.pypi.loader import PyPILoader
from swh.model import hashutil

from .common import RESOURCES_PATH, PyPIClientWithCache


_LOADER_TESTS_CONFIG = {
    'cache': False,
    'cache_dir': '',
    'content_packet_size': 10000,
    'content_packet_size_bytes': 104857600,
    'content_size_limit': 104857600,
    'debug': False,
    'directory_packet_size': 25000,
    'log_db': 'dbname=softwareheritage-log',
    'occurrence_packet_size': 100000,
    'release_packet_size': 100000,
    'revision_packet_size': 100000,
    'save_data': False,
    'save_data_path': '',
    'send_contents': True,
    'send_directories': True,
    'send_releases': True,
    'send_revisions': True,
    'send_snapshot': True,
    'storage': {'args': {}, 'cls': 'memory'},
    'temp_directory': '/tmp/swh.loader.pypi/'
}


class PyPILoaderTest(PyPILoader):
    """Real PyPILoader for test purposes (storage and pypi interactions
       inhibited)

    """
    def __init__(self, project_name, json_filename=None):
        if not json_filename:  # defaulting to using same name as project
            json_filename = '%s.json' % project_name
        project_metadata_file = '%s/%s' % (RESOURCES_PATH, json_filename)
        project_metadata_url = 'https://pypi.org/pypi/%s/json' % project_name
        with open(project_metadata_file) as f:
            data = json.load(f)

        self.temp_dir = tempfile.mkdtemp(
            dir='/tmp/', prefix='swh.loader.pypi.tests-')
        # Will use the pypi with cache
        client = PyPIClientWithCache(
            temp_directory=self.temp_dir, cache_dir=RESOURCES_PATH)
        super().__init__(client=client)
        self.project = PyPIProject(
            client=client,
            project=project_name,
            project_metadata_url=project_metadata_url,
            data=data)

    def parse_config_file(self, *args, **kwargs):
        return _LOADER_TESTS_CONFIG

    def prepare(self, project_name, origin_url,
                origin_metadata_url=None):
        self.project_name = project_name
        self.origin_url = origin_url
        self.origin_metadata_url = origin_metadata_url
        self.visit = 1  # first visit
        self._prepare_state()


@pytest.mark.fs
class PyPIBaseLoaderTest(BaseLoaderTest):
    """Loader Test Mixin to prepare the pypi to 'load' in a test context.

    In this setup, the loader uses the cache to load data so no
    network interaction (no storage, no pypi).

    """
    def setUp(self, project_name='0805nexter',
              dummy_pypi_instance='https://dummy.org'):
        self.tmp_root_path = tempfile.mkdtemp(
            dir='/tmp', prefix='swh.loader.pypi.tests-')
        self._project = project_name
        self._origin_url = '%s/pypi/%s/' % (dummy_pypi_instance, project_name)
        self._project_metadata_url = '%s/pypi/%s/json' % (
            dummy_pypi_instance, project_name)


class PyPILoaderNoSnapshot(PyPILoaderTest):
    """Same as PyPILoaderTest with no prior snapshot seen

    """
    def _last_snapshot(self):
        return None


class LoaderITest(PyPIBaseLoaderTest):
    def setUp(self, project_name='0805nexter',
              dummy_pypi_instance='https://dummy.org'):
        super().setUp(project_name, dummy_pypi_instance)
        self.loader = PyPILoaderNoSnapshot(project_name=project_name)
        self.storage = self.loader.storage

    def test_load(self):
        """Load a pypi origin

        """
        # when
        self.loader.load(
            self._project, self._origin_url, self._project_metadata_url)

        # then
        self.assertCountContents(
            6, '3 contents per release artifact files (2)')
        self.assertCountDirectories(4)
        self.assertCountRevisions(
            2, '2 releases so 2 revisions should be created')
        self.assertCountReleases(0, 'No release is created in the pypi loader')
        self.assertCountSnapshots(1, 'Only 1 snapshot targeting all revisions')

        expected_contents = [
            'a61e24cdfdab3bb7817f6be85d37a3e666b34566',
            '938c33483285fd8ad57f15497f538320df82aeb8',
            'a27576d60e08c94a05006d2e6d540c0fdb5f38c8',
            '405859113963cb7a797642b45f171d6360425d16',
            'e5686aa568fdb1d19d7f1329267082fe40482d31',
            '83ecf6ec1114fd260ca7a833a2d165e71258c338',
        ]

        self.assertContentsContain(expected_contents)

        expected_directories = [
            '05219ba38bc542d4345d5638af1ed56c7d43ca7d',
            'cf019eb456cf6f78d8c4674596f1c9a97ece8f44',
            'b178b66bd22383d5f16f4f5c923d39ca798861b4',
            'c3a58f8b57433a4b56caaa5033ae2e0931405338',
        ]
        self.assertDirectoriesContain(expected_directories)

        # {revision hash: directory hash}
        expected_revisions = {
            '4c99891f93b81450385777235a37b5e966dd1571': '05219ba38bc542d4345d5638af1ed56c7d43ca7d',  # noqa
            'e445da4da22b31bfebb6ffc4383dbf839a074d21': 'b178b66bd22383d5f16f4f5c923d39ca798861b4',  # noqa
        }
        self.assertRevisionsContain(expected_revisions)

        expected_branches = {
            'releases/1.1.0': {
                'target': '4c99891f93b81450385777235a37b5e966dd1571',
                'target_type': 'revision',
            },
            'releases/1.2.0': {
                'target': 'e445da4da22b31bfebb6ffc4383dbf839a074d21',
                'target_type': 'revision',
            },
            'HEAD': {
                'target': 'releases/1.2.0',
                'target_type': 'alias',
            },
        }

        self.assertSnapshotEqual('ba6e158ada75d0b3cfb209ffdf6daa4ed34a227a',
                                 expected_branches)

        self.assertEqual(self.loader.load_status(), {'status': 'eventful'})
        self.assertEqual(self.loader.visit_status(), 'full')


class PyPILoaderWithSnapshot(PyPILoaderTest):
    """This loader provides a snapshot and lists corresponding seen
       release artifacts.

    """
    def _last_snapshot(self):
        """Return last visited snapshot"""
        return {
            'id': b'\xban\x15\x8a\xdau\xd0\xb3\xcf\xb2\t\xff\xdfm\xaaN\xd3J"z',  # noqa
            'branches': {
                b'releases/1.1.0': {
                    'target': b'L\x99\x89\x1f\x93\xb8\x14P'
                    b'8Ww#Z7\xb5\xe9f\xdd\x15q',
                    'target_type': 'revision'
                },
                b'releases/1.2.0': {
                    'target': b'\xe4E\xdaM\xa2+1\xbf'
                    b'\xeb\xb6\xff\xc48=\xbf\x83'
                    b'\x9a\x07M!',
                    'target_type': 'revision'
                },
                b'HEAD': {
                    'target': b'releases/1.2.0',
                    'target_type': 'alias'
                },
            },
        }

    def _known_artifacts(self, last_snapshot):
        """List corresponding seen release artifacts"""
        return {
            (
                '0805nexter-1.1.0.zip',
                '52cd128ad3afe539478abc7440d4b043384295fbe6b0958a237cb6d926465035'  # noqa
            ): b'L\x99\x89\x1f\x93\xb8\x14P8Ww#Z7\xb5\xe9f\xdd\x15q',
            (
                '0805nexter-1.2.0.zip',
                '49785c6ae39ea511b3c253d7621c0b1b6228be2f965aca8a491e6b84126d0709'  # noqa
            ): b'\xe4E\xdaM\xa2+1\xbf\xeb\xb6\xff\xc48=\xbf\x83\x9a\x07M!',
        }


class LoaderNoNewChangesSinceLastVisitITest(PyPIBaseLoaderTest):
    """This scenario makes use of the incremental nature of the loader.

    If nothing changes in between visits, the snapshot for the visit
    must stay the same as the first visit.

    """
    def setUp(self, project_name='0805nexter',
              dummy_pypi_instance='https://dummy.org'):
        super().setUp(project_name, dummy_pypi_instance)
        self.loader = PyPILoaderWithSnapshot(project_name=project_name)
        self.storage = self.loader.storage

    def test_load(self):
        """Load a PyPI origin without new changes results in 1 same snapshot

        """
        # when
        self.loader.load(
            self._project, self._origin_url, self._project_metadata_url)

        # then
        self.assertCountContents(0)
        self.assertCountDirectories(0)
        self.assertCountRevisions(0)
        self.assertCountReleases(0)
        self.assertCountSnapshots(1)

        self.assertContentsContain([])
        self.assertDirectoriesContain([])
        self.assertRevisionsContain(expected_revisions={})

        expected_snapshot_id = 'ba6e158ada75d0b3cfb209ffdf6daa4ed34a227a'
        expected_branches = {
            'releases/1.1.0': {
                'target': '4c99891f93b81450385777235a37b5e966dd1571',
                'target_type': 'revision',
            },
            'releases/1.2.0': {
                'target': 'e445da4da22b31bfebb6ffc4383dbf839a074d21',
                'target_type': 'revision',
            },
            'HEAD': {
                'target': 'releases/1.2.0',
                'target_type': 'alias',
            },
        }
        self.assertSnapshotEqual(expected_snapshot_id, expected_branches)

        _id = hashutil.hash_to_hex(self.loader._last_snapshot()['id'])
        self.assertEqual(expected_snapshot_id, _id)

        self.assertEqual(self.loader.load_status(), {'status': 'uneventful'})
        self.assertEqual(self.loader.visit_status(), 'full')


class LoaderNewChangesSinceLastVisitITest(PyPIBaseLoaderTest):
    """In this scenario, a visit has already taken place.
    An existing snapshot exists.

    This time, the PyPI project has changed, a new release (with 1 new
    release artifact) has been uploaded. The old releases did not
    change.

    The visit results in a new snapshot.

    The new snapshot shares the same history as prior visit's
    snapshot. It holds a new branch targeting the new revision.

    """
    def setUp(self, project_name='0805nexter',
              dummy_pypi_instance='https://dummy.org'):
        super().setUp(project_name, dummy_pypi_instance)
        self.loader = PyPILoaderWithSnapshot(
            project_name=project_name,
            json_filename='0805nexter+new-made-up-release.json')
        self.storage = self.loader.storage

    def test_load(self):
        """Load a PyPI origin with changes results in 1 new snapshot

        """
        # when
        self.loader.load(
            self._project, self._origin_url, self._project_metadata_url)

        # then
        self.assertCountContents(
            4, ("3 + 1 new content (only change between "
                "1.2.0 and 1.3.0 archives)"))
        self.assertCountDirectories(2)
        self.assertCountRevisions(
            1, "1 new revision targeting that new directory id")
        self.assertCountReleases(0)
        self.assertCountSnapshots(1)

        expected_contents = [
            '92689fa2b7fb4d4fc6fb195bf73a50c87c030639',  # new one
            '405859113963cb7a797642b45f171d6360425d16',
            '83ecf6ec1114fd260ca7a833a2d165e71258c338',
            'e5686aa568fdb1d19d7f1329267082fe40482d31',
        ]

        self.assertContentsContain(expected_contents)

        expected_directories = [
            'e226e7e4ad03b4fc1403d69a18ebdd6f2edd2b3a',
            '52604d46843b898f5a43208045d09fcf8731631b',
        ]
        self.assertDirectoriesContain(expected_directories)

        expected_revisions = {
            'fb46e49605b0bbe69f8c53d315e89370e7c6cb5d': 'e226e7e4ad03b4fc1403d69a18ebdd6f2edd2b3a',  # noqa
        }
        self.assertRevisionsContain(expected_revisions)

        old_revisions = {
            '4c99891f93b81450385777235a37b5e966dd1571': '05219ba38bc542d4345d5638af1ed56c7d43ca7d',  # noqa
            'e445da4da22b31bfebb6ffc4383dbf839a074d21': 'b178b66bd22383d5f16f4f5c923d39ca798861b4',  # noqa
        }
        for rev, dir_id in old_revisions.items():
            expected_revisions[rev] = dir_id

        expected_snapshot_id = '07322209e51618410b5e43ca4af7e04fe5113c9d'
        expected_branches = {
            'releases/1.1.0': {
                'target': '4c99891f93b81450385777235a37b5e966dd1571',
                'target_type': 'revision',
            },
            'releases/1.2.0': {
                'target': 'e445da4da22b31bfebb6ffc4383dbf839a074d21',
                'target_type': 'revision',
            },
            'releases/1.3.0': {
                'target': 'fb46e49605b0bbe69f8c53d315e89370e7c6cb5d',
                'target_type': 'revision',
            },
            'HEAD': {
                'target': 'releases/1.3.0',
                'target_type': 'alias',
            },
        }

        self.assertSnapshotEqual(expected_snapshot_id, expected_branches)

        _id = hashutil.hash_to_hex(self.loader._last_snapshot()['id'])
        self.assertNotEqual(expected_snapshot_id, _id)

        self.assertEqual(self.loader.load_status(), {'status': 'eventful'})
        self.assertEqual(self.loader.visit_status(), 'full')


class PyPILoaderWithSnapshot2(PyPILoaderTest):
    """This loader provides a snapshot and lists corresponding seen
       release artifacts.

    """
    def _last_snapshot(self):
        """Return last visited snapshot"""
        return {
            'id': b'\x072"\t\xe5\x16\x18A\x0b^C\xcaJ\xf7\xe0O\xe5\x11<\x9d',  # noqa
            'branches': {
                b'releases/1.1.0': {
                    'target': b'L\x99\x89\x1f\x93\xb8\x14P8Ww#Z7\xb5\xe9f\xdd\x15q',  # noqa
                    'target_type': 'revision'
                },
                b'releases/1.2.0': {
                    'target': b'\xe4E\xdaM\xa2+1\xbf\xeb\xb6\xff\xc48=\xbf\x83\x9a\x07M!',  # noqa
                    'target_type': 'revision'
                },
                b'releases/1.3.0': {
                    'target': b'\xfbF\xe4\x96\x05\xb0\xbb\xe6\x9f\x8cS\xd3\x15\xe8\x93p\xe7\xc6\xcb]',  # noqa
                    'target_type': 'revision'
                },
                b'HEAD': {
                    'target': b'releases/1.3.0',  # noqa
                    'target_type': 'alias'
                },
            }
        }

    def _known_artifacts(self, last_snapshot):
        """Map previously seen release artifacts to their revision"""
        return {
            (
                '0805nexter-1.1.0.zip',
                '52cd128ad3afe539478abc7440d4b043384295fbe6b0958a237cb6d926465035'  # noqa
            ): b'L\x99\x89\x1f\x93\xb8\x14P8Ww#Z7\xb5\xe9f\xdd\x15q',
            (
                '0805nexter-1.2.0.zip',
                '49785c6ae39ea511b3c253d7621c0b1b6228be2f965aca8a491e6b84126d0709'  # noqa
            ): b'\xe4E\xdaM\xa2+1\xbf\xeb\xb6\xff\xc48=\xbf\x83\x9a\x07M!',
            (
                '0805nexter-1.3.0.zip',
                '7097c49fb8ec24a7aaab54c3dbfbb5a6ca1431419d9ee0f6c363d9ad01d2b8b1'  # noqa
            ): b'\xfbF\xe4\x96\x05\xb0\xbb\xe6\x9f\x8cS\xd3\x15\xe8\x93p\xe7\xc6\xcb]',  # noqa
        }


class LoaderChangesOldReleaseArtifactRemovedSinceLastVisit(PyPIBaseLoaderTest):
    """In this scenario, a visit has already taken place.  An existing
    snapshot exists.

    The PyPI project has changed:
    - a new release has been uploaded
    - an older one has been removed

    The visit should result in a new snapshot. Such snapshot shares some of
    the same branches as prior visit (but not all):

    - new release artifact branch exists
    - old release artifact branch has been removed
    - the other unchanged release artifact branches are left unchanged

    """
    def setUp(self, project_name='0805nexter',
              dummy_pypi_instance='https://dummy.org'):
        super().setUp(project_name, dummy_pypi_instance)
        self.loader = PyPILoaderWithSnapshot2(
            project_name=project_name,
            json_filename='0805nexter-unpublished-release.json')
        self.storage = self.loader.storage

    def test_load(self):
        """Load PyPI origin with removed artifact + changes ~> 1 new snapshot

        """
        # when
        self.loader.load(
            self._project, self._origin_url, self._project_metadata_url)

        # then
        self.assertCountContents(
            4, ("3 + 1 new content (only change between "
                "1.3.0 and 1.4.0 archives)"))
        self.assertCountDirectories(2)
        self.assertCountRevisions(
            1, ("This results in 1 new revision targeting "
                "that new directory id"))
        self.assertCountReleases(0)
        self.assertCountSnapshots(1)

        expected_contents = [
            'e2d68a197e3a3ad0fc6de28749077892c2148043',  # new one
            '405859113963cb7a797642b45f171d6360425d16',
            '83ecf6ec1114fd260ca7a833a2d165e71258c338',
            'e5686aa568fdb1d19d7f1329267082fe40482d31',
        ]

        self.assertContentsContain(expected_contents)

        expected_directories = [
            'a2b7621f3e52eb3632657f6e3436bd08202db56f',  # new one
            '770e21215ecac53cea331d8ea4dc0ffc9d979367',
        ]
        self.assertDirectoriesContain(expected_directories)

        expected_revisions = {
            # 1.4.0
            '5e91875f096ac48c98d74acf307439a3490f2827': '770e21215ecac53cea331d8ea4dc0ffc9d979367',  # noqa
        }
        self.assertRevisionsContain(expected_revisions)

        expected_snapshot_id = 'bb0b0c29040678eadb6dae9e43e496cc860123e4'
        expected_branches = {
            'releases/1.2.0': {
                'target': 'e445da4da22b31bfebb6ffc4383dbf839a074d21',
                'target_type': 'revision',
            },
            'releases/1.3.0': {
                'target': 'fb46e49605b0bbe69f8c53d315e89370e7c6cb5d',
                'target_type': 'revision',
            },
            'releases/1.4.0': {
                'target': '5e91875f096ac48c98d74acf307439a3490f2827',
                'target_type': 'revision',
            },
            'HEAD': {
                'target': 'releases/1.4.0',
                'target_type': 'alias',
            },
        }
        self.assertSnapshotEqual(expected_snapshot_id, expected_branches)

        _id = hashutil.hash_to_hex(self.loader._last_snapshot()['id'])
        self.assertNotEqual(expected_snapshot_id, _id)

        self.assertEqual(self.loader.load_status(), {'status': 'eventful'})
        self.assertEqual(self.loader.visit_status(), 'full')

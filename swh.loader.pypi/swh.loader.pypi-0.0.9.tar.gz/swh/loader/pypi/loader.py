# Copyright (C) 2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os
import shutil
from tempfile import mkdtemp

import arrow

from swh.loader.core.utils import clean_dangling_folders
from swh.loader.core.loader import BufferedLoader
from swh.model.from_disk import Directory
from swh.model.identifiers import (
    revision_identifier, snapshot_identifier,
    identifier_to_bytes, normalize_timestamp
)
from swh.storage.algos.snapshot import snapshot_get_all_branches

from .client import PyPIClient, PyPIProject


TEMPORARY_DIR_PREFIX_PATTERN = 'swh.loader.pypi.'
DEBUG_MODE = '** DEBUG MODE **'


class PyPILoader(BufferedLoader):
    CONFIG_BASE_FILENAME = 'loader/pypi'
    ADDITIONAL_CONFIG = {
        'temp_directory': ('str', '/tmp/swh.loader.pypi/'),
        'cache': ('bool', False),
        'cache_dir': ('str', ''),
        'debug': ('bool', False),  # NOT FOR PRODUCTION
    }

    def __init__(self, client=None):
        super().__init__(logging_class='swh.loader.pypi.PyPILoader')
        self.origin_id = None
        if not client:
            temp_directory = self.config['temp_directory']
            os.makedirs(temp_directory, exist_ok=True)
            self.temp_directory = mkdtemp(
                suffix='-%s' % os.getpid(),
                prefix=TEMPORARY_DIR_PREFIX_PATTERN,
                dir=temp_directory)
            self.pypi_client = PyPIClient(
                temp_directory=self.temp_directory,
                cache=self.config['cache'],
                cache_dir=self.config['cache_dir'])
        else:
            self.temp_directory = client.temp_directory
            self.pypi_client = client
        self.debug = self.config['debug']
        self.done = False

    def pre_cleanup(self):
        """To prevent disk explosion if some other workers exploded
        in mid-air (OOM killed), we try and clean up dangling files.

        """
        if self.debug:
            self.log.warn('%s Will not pre-clean up temp dir %s' % (
                DEBUG_MODE, self.temp_directory
            ))
            return
        clean_dangling_folders(self.config['temp_directory'],
                               pattern_check=TEMPORARY_DIR_PREFIX_PATTERN,
                               log=self.log)

    def cleanup(self):
        """Clean up temporary disk use

        """
        if self.debug:
            self.log.warn('%s Will not clean up temp dir %s' % (
                DEBUG_MODE, self.temp_directory
            ))
            return
        if os.path.exists(self.temp_directory):
            self.log.debug('Clean up %s' % self.temp_directory)
            shutil.rmtree(self.temp_directory)

    def prepare_origin_visit(self, project_name, project_url,
                             project_metadata_url=None):
        """Prepare the origin visit information

        Args:
            project_name (str): Project's simple name
            project_url (str): Project's main url
            project_metadata_url (str): Project's metadata url

        """
        self.origin = {
            'url': project_url,
            'type': 'pypi',
        }
        self.visit_date = None  # loader core will populate it

    def _known_artifacts(self, last_snapshot):
        """Retrieve the known releases/artifact for the origin_id.

        Args
            snapshot (dict): Last snapshot for the visit

        Returns:
            list of (filename, sha256) tuples.

        """
        if not last_snapshot or 'branches' not in last_snapshot:
            return {}

        # retrieve only revisions (e.g the alias we do not want here)
        revs = [rev['target']
                for rev in last_snapshot['branches'].values()
                if rev and rev['target_type'] == 'revision']
        known_revisions = self.storage.revision_get(revs)
        ret = {}
        for revision in known_revisions:
            if not revision:  # revision_get can return None
                continue
            if 'original_artifact' in revision['metadata']:
                artifact = revision['metadata']['original_artifact']
                ret[artifact['filename'], artifact['sha256']] = revision['id']
        return ret

    def _last_snapshot(self):
        """Retrieve the last snapshot

        """
        snapshot = self.storage.snapshot_get_latest(self.origin_id)
        if snapshot and snapshot.pop('next_branch', None):
            snapshot = snapshot_get_all_branches(self.storage, snapshot['id'])
        return snapshot

    def prepare(self, project_name, project_url,
                project_metadata_url=None):
        """Keep reference to the origin url (project) and the
           project metadata url

        Args:
            project_name (str): Project's simple name
            project_url (str): Project's main url
            project_metadata_url (str): Project's metadata url

        """
        self.project_name = project_name
        self.origin_url = project_url
        self.project_metadata_url = project_metadata_url
        self.project = PyPIProject(self.pypi_client, self.project_name,
                                   self.project_metadata_url)
        self._prepare_state()

    def _prepare_state(self):
        """Initialize internal state (snapshot, contents, directories, etc...)

        This is called from `prepare` method.

        """
        last_snapshot = self._last_snapshot()
        self.known_artifacts = self._known_artifacts(last_snapshot)
        # and the artifacts
        # that will be the source of data to retrieve
        self.new_artifacts = self.project.download_new_releases(
            self.known_artifacts
        )
        # temporary state
        self._contents = []
        self._directories = []
        self._revisions = []
        self._load_status = 'uneventful'
        self._visit_status = 'full'

    def fetch_data(self):
        """Called once per release artifact version (can be many for one
           release).

        This will for each call:
        - retrieve a release artifact (associated to a release version)
        - Uncompress it and compute the necessary information
        - Computes the swh objects

        Returns:
            True as long as data to fetch exist

        """
        data = None
        if self.done:
            return False

        try:
            data = next(self.new_artifacts)
            self._load_status = 'eventful'
        except StopIteration:
            self.done = True
            return False

        project_info, author, release, artifact, dir_path = data
        dir_path = dir_path.encode('utf-8')
        directory = Directory.from_disk(path=dir_path, data=True)
        _objects = directory.collect()

        self._contents = _objects['content'].values()
        self._directories = _objects['directory'].values()
        date = normalize_timestamp(
            int(arrow.get(artifact['date']).timestamp))

        name = release['name'].encode('utf-8')
        message = release['message'].encode('utf-8')
        if message:
            message = b'%s: %s' % (name, message)
        else:
            message = name

        _revision = {
            'synthetic': True,
            'metadata': {
                'original_artifact': artifact,
                'project': project_info,
            },
            'author': author,
            'date': date,
            'committer': author,
            'committer_date': date,
            'message': message,
            'directory': directory.hash,
            'parents': [],
            'type': 'tar',
        }
        _revision['id'] = identifier_to_bytes(
            revision_identifier(_revision))
        self._revisions.append(_revision)

        artifact_key = artifact['filename'], artifact['sha256']
        self.known_artifacts[artifact_key] = _revision['id']

        return not self.done

    def target_from_artifact(self, filename, sha256):
        target = self.known_artifacts.get((filename, sha256))
        if target:
            return {
                'target': target,
                'target_type': 'revision',
            }
        return None

    def generate_and_load_snapshot(self):
        branches = {}
        for release, artifacts in self.project.all_release_artifacts().items():
            default_release = self.project.default_release()
            if len(artifacts) == 1:
                # Only one artifact for this release, generate a single branch
                branch_name = 'releases/%s' % release
                filename, sha256 = artifacts[0]
                target = self.target_from_artifact(filename, sha256)
                branches[branch_name.encode('utf-8')] = target
                if release == default_release:
                    branches[b'HEAD'] = {
                        'target_type': 'alias',
                        'target': branch_name.encode('utf-8'),
                    }
                if not target:
                    self._visit_status = 'partial'
            else:
                # Several artifacts for this release, generate a separate
                # pointer for each of them
                for filename, sha256 in artifacts:
                    branch_name = 'releases/%s/%s' % (release, filename)
                    target = self.target_from_artifact(filename, sha256)
                    branches[branch_name.encode('utf-8')] = target
                    if not target:
                        self._visit_status = 'partial'

        snapshot = {
            'branches': branches,
        }
        snapshot['id'] = identifier_to_bytes(
            snapshot_identifier(snapshot))
        self.maybe_load_snapshot(snapshot)

    def store_data(self):
        """(override) This sends collected objects to storage.

        """
        self.maybe_load_contents(self._contents)
        self.maybe_load_directories(self._directories)
        self.maybe_load_revisions(self._revisions)

        if self.done:
            self.generate_and_load_snapshot()
            self.flush()

    def load_status(self):
        return {
            'status': self._load_status,
        }

    def visit_status(self):
        return self._visit_status


if __name__ == '__main__':
    import logging
    import sys
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) != 2:
        logging.error('Usage: %s <module-name>' % sys.argv[0])
        sys.exit(1)
    module_name = sys.argv[1]
    loader = PyPILoader()
    loader.load(
        module_name,
        'https://pypi.org/projects/%s/' % module_name,
        'https://pypi.org/pypi/%s/json' % module_name,
    )

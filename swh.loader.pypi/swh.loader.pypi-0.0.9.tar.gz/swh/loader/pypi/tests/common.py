# Copyright (C) 2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import json
import shutil
import os
import tempfile

import pytest
from unittest import TestCase

from swh.loader.pypi.client import PyPIClient, PyPIProject


RESOURCES_PATH = './swh/loader/pypi/tests/resources'


class PyPIClientWithCache(PyPIClient):
    """Force the use of the cache to bypass pypi calls

    """
    def __init__(self, temp_directory, cache_dir):
        super().__init__(temp_directory=temp_directory,
                         cache=True, cache_dir=cache_dir)


@pytest.mark.fs
class WithProjectTest(TestCase):
    def setUp(self):
        project = '0805nexter'
        project_metadata_file = '%s/%s.json' % (RESOURCES_PATH, project)

        with open(project_metadata_file) as f:
            data = json.load(f)

        temp_dir = tempfile.mkdtemp(
            dir='/tmp/', prefix='swh.loader.pypi.tests-')
        project_metadata_url = 'https://pypi.org/pypi/%s/json' % project
        # Will use the pypi with cache
        client = PyPIClientWithCache(
            temp_directory=temp_dir, cache_dir=RESOURCES_PATH)
        self.project = PyPIProject(
            client=client,
            project=project,
            project_metadata_url=project_metadata_url,
            data=data)

        self.data = data
        self.temp_dir = temp_dir
        self.project_name = project

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

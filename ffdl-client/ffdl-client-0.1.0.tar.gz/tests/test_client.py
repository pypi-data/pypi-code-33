#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ffdl-python-client` package."""

import os
import unittest
from pprint import pprint

from ffdl.client import Config, FfDLClient

DEFAULT_FFDL_API_ENDPOINT = os.getenv('FFDL_API_ENDPOINT')
DEFAULT_FFDL_USER = os.getenv('FFDL_USER')
DEFAULT_FFDL_PASSWORD = os.getenv('FFDL_PASSWORD')
DEFAULT_FFDL_USER_INFO = os.getenv('FFDL_USER_INFO')

RESOURCES = os.path.join(os.path.dirname(__file__), 'resources')


class TestEnterpriseScheduler(unittest.TestCase):
    """Tests for `ffdl-python-client` package."""
    client = None

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures, if any."""
        config = Config(api_endpoint=DEFAULT_FFDL_API_ENDPOINT,
                        user=DEFAULT_FFDL_USER,
                        password=DEFAULT_FFDL_PASSWORD,
                        user_info=DEFAULT_FFDL_USER_INFO)

        cls.client = FfDLClient(config)

    def test_submit_job(self):
        url = '/models'

        file_paths = \
            {'model_definition':
             str(os.path.join(RESOURCES, 'ffdl-9c29897d.zip')),
             'manifest':
             str(os.path.join(RESOURCES, 'manifest-9c29897d.yml'))}

        result = self.client.post(url, **file_paths)

        pprint(result)

    def test_get_training_jobs_list(self):
        url = '/models'

        result = self.client.get(url)

        self.assertGreater(len(result['models']),  0)

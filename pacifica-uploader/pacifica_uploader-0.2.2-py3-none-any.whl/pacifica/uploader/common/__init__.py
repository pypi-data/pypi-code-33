#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Common uploader functionality."""
from os import getenv
import requests


# pylint: disable=too-few-public-methods
class CommonBase(object):
    """Contains methods to implement common functionality."""

    session = None

    def _setup_requests_session(self):
        """Setup a requests retry session so we can talk to http services."""
        self.session = requests.session()
        retry_adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.session.mount('https://', retry_adapter)
        self.session.mount('http://', retry_adapter)

    def _server_url(self, parts, env_prefix, kwargs):
        """Server URL parsing for init class method."""
        for part, default in parts:
            attr_name = '_{}'.format(part)
            setattr(self, attr_name, kwargs.get(part))
            if not getattr(self, attr_name):
                setattr(self, attr_name, getenv('{}{}'.format(
                    env_prefix, attr_name.upper()), default))
# pylint: enable=too-few-public-methods

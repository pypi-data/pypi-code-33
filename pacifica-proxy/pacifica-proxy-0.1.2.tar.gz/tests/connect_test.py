#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the connections to external service."""
from unittest import TestCase
from json import dumps
import httpretty
from pacifica.proxy.config import get_config
from pacifica.proxy.__main__ import try_meta_connect


class TestMetaConnect(TestCase):
    """Test the metadata connection."""

    @httpretty.activate
    def test_meta_connect(self):
        """Test the try meta connect method."""
        st_url = get_config().get('metadata', 'status_url')
        httpretty.register_uri(httpretty.GET, st_url,
                               body=dumps([]),
                               content_type='application/json')
        try_meta_connect(0)
        self.assertEqual(httpretty.last_request().method, 'GET')

    @httpretty.activate
    def test_meta_connect_failure(self):
        """Test the try meta connect method but fail."""
        st_url = get_config().get('metadata', 'status_url')
        httpretty.register_uri(httpretty.GET, st_url,
                               body='',
                               status=500,
                               content_type='application/json')
        hit_exception = False
        try:
            try_meta_connect(39)
        # pylint: disable=broad-except
        except Exception:
            hit_exception = True
        # pylint: enable=broad-except
        self.assertTrue(hit_exception)
        self.assertEqual(httpretty.last_request().method, 'GET')

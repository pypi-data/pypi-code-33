#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the events policy."""
from os.path import join
from json import loads
from cherrypy.test import helper
from common_test import CommonCPSetup


class TestEventsPolicy(helper.CPWebCase, CommonCPSetup):
    """Test the Events policy service."""

    PORT = 8181
    HOST = '127.0.0.1'
    headers = [('Content-Type', 'application/json')]

    def test_events_query(self):
        """Test posting the queries."""
        valid_query = loads(
            open(join('test_files', 'events_query.json')).read())
        ret_data = self.get_json_page('/events/dmlb2001', valid_query)
        self.assertFalse(ret_data is None)
        self.assertTrue('status' in ret_data)
        self.assertEqual(ret_data['status'], 'success')

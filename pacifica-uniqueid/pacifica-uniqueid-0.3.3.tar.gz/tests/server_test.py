#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Unique ID unit and integration tests."""
from __future__ import print_function
import requests
import cherrypy
from cherrypy.test import helper
from pacifica.uniqueid.rest import Root, error_page_default
from pacifica.uniqueid.orm import OrmSync, UniqueIndex
from pacifica.uniqueid.globals import CHERRYPY_CONFIG


def uniqueid_droptables(func):
    """Setup the database and drop it once done."""
    def wrapper(*args, **kwargs):
        """Create the database table."""
        OrmSync.update_tables()
        func(*args, **kwargs)
        UniqueIndex.drop_table()
    return wrapper


class TestUniqueID(helper.CPWebCase):
    """Test the uniqueid server end to end."""

    HOST = '127.0.0.1'
    PORT = 8051
    url = 'http://127.0.0.1:8051/getid?range={range}&mode={mode}'

    @staticmethod
    def setup_server():
        """Bind tables to in memory db and start service."""
        cherrypy.config.update({'error_page.default': error_page_default})
        cherrypy.config.update(CHERRYPY_CONFIG)
        cherrypy.tree.mount(Root(), '/', CHERRYPY_CONFIG)

    def _url(self, id_range, mode):
        """Return the parsed url."""
        return self.url.format(range=id_range, mode=mode)

    @uniqueid_droptables
    def test_working_stuff(self):
        """Test the good working bits."""
        req = requests.get(self._url(2, 'foo'))
        parts = req.json()
        self.assertTrue('endIndex' in parts)
        self.assertTrue('startIndex' in parts)
        self.assertEqual(parts['startIndex'], 1)
        self.assertEqual(parts['endIndex'], 2)

        req = requests.get(self._url(10, 'foo'))
        parts = req.json()
        self.assertTrue('endIndex' in parts)
        self.assertTrue('startIndex' in parts)
        self.assertEqual(parts['startIndex'], 3)
        self.assertEqual(parts['endIndex'], 12)

        req = requests.get(self._url('blah', 'foo'))
        self.assertEqual(req.status_code, 500)

        req = requests.get('http://127.0.0.1:8051/blah')
        self.assertEqual(req.status_code, 404)

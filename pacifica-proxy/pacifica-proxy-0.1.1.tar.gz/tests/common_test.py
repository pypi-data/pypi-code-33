#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Common server setup code for CherryPy testing."""
import logging
import cherrypy
from pacifica.proxy.rest import Root, error_page_default
from pacifica.proxy.globals import CHERRYPY_CONFIG


# pylint: disable=too-few-public-methods
class CommonCPSetup(object):
    """Common CherryPy setup class."""

    @staticmethod
    def setup_server():
        """Setup each test by starting the CherryPy server."""
        logger = logging.getLogger('urllib2')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
        cherrypy.config.update({'error_page.default': error_page_default})
        cherrypy.config.update(CHERRYPY_CONFIG)
        cherrypy.tree.mount(Root(), '/', CHERRYPY_CONFIG)
# pylint: enable=too-few-public-methods

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy root object."""
import json
import cherrypy
from .files import Files


def error_page_default(**kwargs):
    """The default error page should always enforce json."""
    cherrypy.response.headers['Content-Type'] = 'application/json'
    return json.dumps({
        'status': kwargs['status'],
        'message': kwargs['message'],
        'traceback': kwargs['traceback'],
        'version': kwargs['version']
    })

# pylint: disable=too-few-public-methods


class Root(object):
    """
    CherryPy root object class.

    not exposed by default the base objects are exposed
    """

    exposed = False

    def __init__(self):
        """Create the local objects we need."""
        self.files = Files()
# pylint: enable=too-few-public-methods

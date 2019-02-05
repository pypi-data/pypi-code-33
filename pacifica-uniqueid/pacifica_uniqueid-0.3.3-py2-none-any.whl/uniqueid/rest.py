#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""UniqueID CherryPy Module."""
from __future__ import print_function
from json import dumps
import cherrypy
from .orm import UniqueIndex, update_index


def error_page_default(**kwargs):
    """The default error page should always enforce json."""
    cherrypy.response.headers['Content-Type'] = 'application/json'
    return dumps({
        'status': kwargs['status'],
        'message': kwargs['message'],
        'traceback': kwargs['traceback'],
        'version': kwargs['version']
    })


# pylint: disable=too-few-public-methods
class GetID(object):
    """CherryPy GetID object."""

    exposed = True

    # pylint: disable=invalid-name
    @staticmethod
    @cherrypy.tools.json_out()
    def GET(**kwargs):
        """Get an id range for the mode."""
        UniqueIndex.database_connect()
        id_range = int(kwargs.get('range', -1))
        id_mode = kwargs.get('mode', -1)
        index, id_range = update_index(id_range, id_mode)
        UniqueIndex.database_close()
        return {'startIndex': index, 'endIndex': index + id_range - 1}
    # pylint: enable=invalid-name


class Root(object):
    """CherryPy Root object."""

    exposed = False
    getid = GetID()
# pylint: enable=too-few-public-methods

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy files proxy."""
from json import loads
import requests
import cherrypy
from .config import get_config


class Files(object):
    """
    CherryPy files object class.

    This object proxies requests to the archive interface service
    based on the files hashsum instead of ID.
    """

    exposed = True

    @staticmethod
    def nginx_accel(the_file):
        """Use nginx to accelerate the transfer of the file."""
        cherrypy.response.headers.update({
            'X-Accel-Redirect': '/archivei_accel/{0}'.format(the_file['_id']),
            'Content-Disposition': 'attachment; filename={0}'.format(the_file['name']),
            'Content-Type': 'application/octet-stream'
        })
        return ''

    @staticmethod
    def stream_the_file(the_file):
        """Stream the file yourself."""
        resp = requests.get(
            '{0}/{1}'.format(
                get_config().get('archiveinterface', 'url'),
                the_file['_id']
            ),
            stream=True
        )
        mime = 'application/octet-stream'
        response = cherrypy.serving.response
        response.headers['Content-Type'] = mime
        disposition = 'attachment'
        contentd = '%s; filename="%s"' % (disposition, the_file['name'])
        response.headers['Content-Disposition'] = contentd
        # pylint: disable=protected-access
        return cherrypy.lib.static._serve_fileobj(resp.raw, mime, int(the_file['size']), True)
        # pylint: enable=protected-access

    # pylint: disable=invalid-name
    @staticmethod
    def GET(hashtype, hashsum):
        """Create the local objects we need."""
        files = loads(
            requests.get(
                '{0}/files?hashsum={1}&hashtype={2}'.format(
                    get_config().get('metadata', 'url'),
                    hashsum,
                    hashtype
                )
            ).text
        )

        if not files:
            raise cherrypy.HTTPError('404 Not Found', 'File does not exist.')
        the_file = files[0]
        if get_config().getboolean('nginx', 'accel'):
            return Files.nginx_accel(the_file)
        return Files.stream_the_file(the_file)
    # pylint: enable=invalid-name


# The only HTML file we serve that isn't a template, index.html, should have an
# etag and be checked each time.  Items inside all have a version as part of the
# filename, so reloading this one HTML file updates the site.
#
# All vendor files should have the version manually appended when adding to the
# project or upgrading versions.
#
# To ensure an incremental build that only updates one of the generated files
# works, the build scripts should always regenerate the index HTML too.

# WARNING
# -------
#
# Python's asyncio does not have an asynchronous way to read files because operating systems
# don't really support it.  Apparently *nix systems have the API (select with file descriptors)
# but they always report themselves ready and therefore end up blocking anyway.
#
# Python will soon (or may already) support an asynchronous sendfile, which would could try to
# use.
#
# To work around this, we'll simply cache the files in memory.  Due to reference counting,
# Python is usually very good with memory.  The library is really designed for single page
# applications where resources are cached at the browser for a year.  (Put your version number
# on the end!)

# TODO ITEMS
# ----------
#
# We have not implemented compression yet.  I don't believe there are any modern browsers that
# don't support gzip, so we should only support compression and hold the compressed version in
# memory.
#
# Add a way to register mimetypes.  (Or perhaps use a module that already has them?)

import re, gzip, os
from os.path import isdir, splitext, abspath, join, exists, isabs
from logging import getLogger
from .errors import HttpError
from asyncio import coroutine
from collections import namedtuple
from datetime import timedelta

from .routing import Route, register_route

logger = getLogger('static')

USE_CACHE = (os.environ.get('SERVANT_STATIC_CACHE', '1').lower() in ('1', 'true', 't'))
logger.debug('caching: %s', USE_CACHE)

Ext = namedtuple('Ext', 'mimetype compress')
map_ext_to_mime = {
    '.css'  : Ext('text/css', True),
    '.eot'  : Ext('application/vnd.ms-fontobject', True),
    '.gif'  : Ext('image/gif' , False),
    '.html' : Ext('text/html', True),
    '.ico'  : Ext('image/ico', False),
    '.jpe'  : Ext('image/jpeg', False),
    '.jpeg' : Ext('image/jpeg', False),
    '.jpg'  : Ext('image/jpeg', False),
    '.js'   : Ext('text/javascript', True),
    '.map'  : Ext('application/json', True),
    '.otf'  : Ext('application/x-font-otf', True),
    '.png'  : Ext('image/png', False),
    '.svg'  : Ext('image/svg+xml', True),
    '.ttf'  : Ext('application/x-font-ttf', True),
    '.woff' : Ext('application/font-woff', False),
    '.woff2': Ext('application/font-woff2', False)
}

re_dots = re.compile(r'(^|/)\.{1,2}(/|$)')
# A regular expression that matches ".." as a subdirectory (component) of a URL
# (../, /../, or /..).  This is not allowed.

routes = []
# Routes registered for static route prefixes, in the order they were registered.

class File:
    def __init__(self, relpath, mimetype, content, compressed, *, cache_control):
        self.relpath    = relpath
        self.mimetype   = mimetype
        self.content    = content
        self.compressed = compressed # True if gzipped
        self.etag       = None
        self.cache_control = cache_control


class StaticFileRoute(Route):
    """
    A route for serving static files from the static file cache.
    """
    def __init__(self, prefix, path, cache_control=None, route_keywords=None, name=None):
        """
        prefix
          The URL prefix.

        path
          The directory to load files from for URLs that start with the given prefix.

        cache_control
          The value to set for the cache-control header.  If not provided the
          header is not added.

        name
          An optional name for this route so it can be looked up later.
        """
        Route.__init__(self, route_keywords=route_keywords, method='GET')

        self.prefix = prefix
        self.path   = path
        self.name   = name

        self.cache_control = cache_control

        if prefix[-1] != '/':
            prefix += '/'

        self.regexp = self._prefix_to_regexp(prefix)

        self.cache = {}
        # Maps from relative path (from self.path) to a FileEntry object.  Used
        # when USE_CACHE is true.

    def __repr__(self):
        return 'StaticFileRoute<%s>' % self.prefix

    def _prefix_to_regexp(self, prefix):
        """
        Given a prefix being registered, convert it to a regular expression that
        matches the entire URL.  It should have a single group that matches
        everything after the prefix (and after the slash separating the prefix from
        the relative path).

        The special character '*' can be used to represent a subdirectory whose
        value is ignored.  This can be useful for ignoring version components of
        paths.  The star must be by itself and not mixed with letters.  For example
        "/static/*/img" and "/js/*" is accepted, but not "/static/x*/img".
        """
        # Escape all of the "normal" parts.  The only non-normal we support right
        # now is "*" which represents a subdirectory.
        parts = prefix.rstrip('/').split('/')
        parts = [ (re.escape(p) if p != '*' else '[^/]+') for p in parts ]

        regexp = '^' + '/'.join(parts) + '/(.+)$'

        return re.compile(regexp)

    def _getfile(self, relpath):
        """
        Returns an http.File object for the given self.path / relpath combination.
        """
        fqn = abspath(join(self.path, relpath))
        if not exists(fqn):
            logger.debug('Not found: url=%r fqn=%r', relpath, fqn)
            raise HttpError(404, url=relpath)

        if re_dots.search(relpath):
            # This means someone used ".." to try to move up out of the static directory.  This
            # very well may be a hack attempt.
            logger.error('SECURITY: Dangerous path in file download?  prefix=%s self.path=%s relpath=%s fqn=%s',
                        self.prefix, self.path, relpath, fqn)
            raise HttpError(404, url=relpath)

        ext = splitext(relpath)[1]
        if ext not in map_ext_to_mime:
            raise Exception('No mimetype for "{}" (from {!r})'.format(ext, relpath))

        content = open(fqn, 'rb').read()
        extinfo = map_ext_to_mime[ext]

        if extinfo.compress:
            content = gzip.compress(content)

        entry = File(relpath, extinfo.mimetype, content, extinfo.compress, cache_control=self.cache_control)

        return entry

    def get(self, relpath):
        """
        Returns the file, adding to the cache if necessary.
        """
        f = USE_CACHE and self.cache.get(relpath)
        if not f:
            f = self._getfile(relpath)

            if USE_CACHE:
                self.cache[relpath] = f

        return f

    @coroutine
    def __call__(self, match, ctx):
        relpath = match.group(1)
        return self.get(relpath)


def register_file_type(ext, mimetype=None, compress=None):
    map_ext_to_mime[ext] = Ext(mimetype=mimetype, compress=compress)


def serve_prefix(prefix, path, cache_control=None, name=None, **route_keywords):
    """
    Registers a URL prefix (e.g. "/images") with a directory.  Any URLs starting with this
    prefix will serve files from the given path or below.

    route_keywords
      Route keywords.  These are attached to the route for use by middleware.
    """
    assert isabs(path), 'static path {!r} for prefix {} is not absolute'.format(path, prefix)
    assert isdir(path), 'static path {!r} for prefix {} does not exist'.format(path, prefix)

    route = StaticFileRoute(prefix, path, cache_control=cache_control, name=name, route_keywords=route_keywords)
    register_route(route)

    routes.append(route)


def route_from_name(name):
    """
    Returns the route with the given name.  Returns None if not found.
    """
    for route in routes:
        if route.name and route.name == name:
            return route
    return None


def path_from_prefix(prefix):
    """
    Return the directory that files for the given URL prefix are being
    served from.
    """
    if prefix[-1] != '/':
        prefix += '/'

    for route in routes:
        if route.prefix == prefix:
            return route.path
    raise Exception('The prefix {!r} is not being served'.format(prefix))


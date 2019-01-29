#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    "header", "debug",
    "input", "data",
    "setcookie", "cookies",
    "request",
    "HTTPError",

    # 200, 201, 202
    "OK", "Created", "Accepted",
    "ok", "created", "accepted",

    # 301, 302, 303, 304, 307
    "Redirect", "Found", "SeeOther", "NotModified", "TempRedirect",
    "redirect", "found", "seeother", "notmodified", "tempredirect",
    "HttpResponseRedirect",

    # 400, 401, 403, 404, 405, 406, 409, 410, 412, 415
    "BadRequest", "Unauthorized", "Forbidden", "NotFound", "NoMethod", "NotAcceptable", "Conflict", "Gone",
    "PreconditionFailed", "UnsupportedMediaType",
    "badrequest", "unauthorized", "forbidden", "notfound", "nomethod", "notacceptable", "conflict", "gone",
    "preconditionfailed", "unsupportedmediatype",

    # 500
    "InternalError",
    "internalerror",

    "render",
    "HttpResponse", "TemplateResponse",
]

import os, sys, cgi, Cookie, pprint, urlparse, urllib
from pweb import template, conf
from pweb.utils import safestr, intget, dictadd
from pweb.utils.datastructs import storify, threadeddict, storage
from pweb.http.resultstruct import jsonresult, textresult


class HTTPError(Exception):
    def __init__(self, status, headers={}, data=""):
        request.status = status
        for k, v in headers.items():
            header(k, v)
        self.data = data
        Exception.__init__(self, status)


def _status_code(status, data=None, classname=None, docstring=None):
    if data is None: data = status.split(" ", 1)[1]
    classname = status.split(" ", 1)[1].replace(' ', '')  # 304 Not Modified -> NotModified
    docstring = docstring or '`%s` status' % status

    def __init__(self, data=data, headers={}):
        HTTPError.__init__(self, status, headers, data)

    # trick to create class dynamically with dynamic docstring.
    return type(classname, (HTTPError, object), {
        '__doc__': docstring,
        '__init__': __init__
    })


ok = OK = _status_code("200 OK", data="")
created = Created = _status_code("201 Created")
accepted = Accepted = _status_code("202 Accepted")


class Redirect(HTTPError):
    """A `301 Moved Permanently` redirect."""

    def __init__(self, url, status='301 Moved Permanently', absolute=False):
        """
        Returns a `status` redirect to the new URL. 
        `url` is joined with the base URL so that things like 
        `redirect("about") will work properly.
        """
        newloc = urlparse.urljoin(request.path, url)

        if newloc.startswith('/'):
            if absolute:
                home = request.realhome
            else:
                home = request.home
            newloc = home + newloc

        headers = {
            'Content-Type': 'text/html',
            'Location': newloc
        }
        HTTPError.__init__(self, status, headers, "")


redirect = HttpResponseRedirect = Redirect


class Found(Redirect):
    """A `302 Found` redirect."""

    def __init__(self, url, absolute=False):
        Redirect.__init__(self, url, '302 Found', absolute=absolute)


found = Found


class SeeOther(Redirect):
    """A `303 See Other` redirect."""

    def __init__(self, url, absolute=False):
        Redirect.__init__(self, url, '303 See Other', absolute=absolute)


seeother = SeeOther


class NotModified(HTTPError):
    """A `304 Not Modified` status."""

    def __init__(self):
        HTTPError.__init__(self, "304 Not Modified")


notmodified = NotModified


class TempRedirect(Redirect):
    """A `307 Temporary Redirect` redirect."""

    def __init__(self, url, absolute=False):
        Redirect.__init__(self, url, '307 Temporary Redirect', absolute=absolute)


tempredirect = TempRedirect


class BadRequest(HTTPError):
    """`400 Bad Request` error."""
    message = "bad request"

    def __init__(self, message=None):
        status = "400 Bad Request"
        headers = {'Content-Type': 'text/html'}
        HTTPError.__init__(self, status, headers, message or self.message)


badrequest = BadRequest


class Unauthorized(HTTPError):
    """`401 Unauthorized` error."""
    message = "unauthorized"

    def __init__(self):
        status = "401 Unauthorized"
        headers = {'Content-Type': 'text/html'}
        HTTPError.__init__(self, status, headers, self.message)


unauthorized = Unauthorized


class Forbidden(HTTPError):
    """`403 Forbidden` error."""
    message = "forbidden"

    def __init__(self):
        status = "403 Forbidden"
        headers = {'Content-Type': 'text/html'}
        HTTPError.__init__(self, status, headers, self.message)


forbidden = Forbidden


class _NotFound(HTTPError):
    """`404 Not Found` error."""
    message = """<head>
<title>Error response</title>
</head>
<body>
<h1>Error response</h1>
<p>Error code 404.
<p>Error code explanation: Nothing matches the given URI..
</body>"""

    def __init__(self, message=None):
        status = '404 Not Found'
        headers = {'Content-Type': 'text/html'}
        HTTPError.__init__(self, status, headers, message or self.message)


def NotFound(message=None):
    """Returns HTTPError with '404 Not Found' error from the active application.
    """
    if message:
        return _NotFound(message)
    else:
        return _NotFound()


notfound = NotFound


class NoMethod(HTTPError):
    """A `405 Method Not Allowed` error."""

    def __init__(self, cls=None):
        status = '405 Method Not Allowed'
        headers = {}
        headers['Content-Type'] = 'text/html'

        methods = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE']
        if cls:
            methods = [method for method in methods if hasattr(cls, method)]

        headers['Allow'] = ', '.join(methods)
        data = None
        HTTPError.__init__(self, status, headers, data)


nomethod = NoMethod


class NotAcceptable(HTTPError):
    """`406 Not Acceptable` error."""
    message = "not acceptable"

    def __init__(self):
        status = "406 Not Acceptable"
        headers = {'Content-Type': 'text/html'}
        HTTPError.__init__(self, status, headers, self.message)


notacceptable = NotAcceptable


class Conflict(HTTPError):
    """`409 Conflict` error."""
    message = "conflict"

    def __init__(self):
        status = "409 Conflict"
        headers = {'Content-Type': 'text/html'}
        HTTPError.__init__(self, status, headers, self.message)


conflict = Conflict


class Gone(HTTPError):
    """`410 Gone` error."""
    message = "gone"

    def __init__(self):
        status = '410 Gone'
        headers = {'Content-Type': 'text/html'}
        HTTPError.__init__(self, status, headers, self.message)


gone = Gone


class PreconditionFailed(HTTPError):
    """`412 Precondition Failed` error."""
    message = "precondition failed"

    def __init__(self):
        status = "412 Precondition Failed"
        headers = {'Content-Type': 'text/html'}
        HTTPError.__init__(self, status, headers, self.message)


preconditionfailed = PreconditionFailed


class UnsupportedMediaType(HTTPError):
    """`415 Unsupported Media Type` error."""
    message = "unsupported media type"

    def __init__(self):
        status = "415 Unsupported Media Type"
        headers = {'Content-Type': 'text/html'}
        HTTPError.__init__(self, status, headers, self.message)


unsupportedmediatype = UnsupportedMediaType


class _InternalError(HTTPError):
    """500 Internal Server Error`."""
    message = "internal server error"

    def __init__(self, message=None):
        status = '500 Internal Server Error'
        headers = {'Content-Type': 'text/html'}
        HTTPError.__init__(self, status, headers, message or self.message)


def InternalError(message=None):
    """Returns HTTPError with '500 internal error' error from the active application.
    """
    if message:
        return _InternalError(message)
    else:
        return _InternalError()


internalerror = InternalError


def header(hdr, value, unique=False):
    hdr, value = safestr(hdr), safestr(value)
    if '\n' in hdr or '\r' in hdr or '\n' in value or '\r' in value:
        raise ValueError, 'invalid characters in header'

    if unique is True:
        if hasattr(request, "headers"):
            for h, v in request.headers:
                if h.lower() == hdr.lower(): return

    try:
        request.headers.append((hdr, value))
    except Exception, e:
        print e


def rawinput(method=None):
    """Returns storage object with GET or POST arguments.
    """
    method = method or "both"
    from cStringIO import StringIO

    def dictify(fs):
        if fs.list is None: fs.list = []
        return dict([(k, fs[k]) for k in fs.keys()])

    e = request.env.copy()
    a = b = {}

    if method.lower() in ['both', 'post', 'put']:
        if e['REQUEST_METHOD'] in ['POST', 'PUT']:
            if e.get('CONTENT_TYPE', '').lower().startswith('multipart/'):
                a = request.get('_fieldstorage')
                if not a:
                    fp = e['wsgi.input']
                    a = cgi.FieldStorage(fp=fp, environ=e, keep_blank_values=1)
                    request._fieldstorage = a
            else:
                fp = StringIO(data())
                a = cgi.FieldStorage(fp=fp, environ=e, keep_blank_values=1)
            a = dictify(a)

    if method.lower() in ['both', 'get']:
        e['REQUEST_METHOD'] = 'GET'
        b = dictify(cgi.FieldStorage(environ=e, keep_blank_values=1))

    def process_fieldstorage(fs):
        if isinstance(fs, list):
            return [process_fieldstorage(x) for x in fs]
        elif fs.filename is None:
            return fs.value
        else:
            return fs

    return storage([(k, process_fieldstorage(v)) for k, v in dictadd(b, a).items()])


def input(*requireds, **defaults):
    _method = defaults.pop('_method', 'both')
    out = rawinput(_method)
    try:
        defaults.setdefault('_unicode', True)  # force unicode conversion by default.
        return storify(out, *requireds, **defaults)
    except KeyError:
        raise badrequest()


def data():
    if 'data' not in request:
        cl = intget(request.env.get('CONTENT_LENGTH'), 0)
        request.data = request.env['wsgi.input'].read(cl)
    return request.data


def setcookie(name, value, expires='', domain=None, secure=False, httponly=False, path=None):
    morsel = Cookie.Morsel()
    name, value = safestr(name), safestr(value)
    morsel.set(name, value, urllib.quote(value))
    if expires < 0: expires = -1000000000
    morsel['expires'] = expires
    morsel['path'] = path or request.homepath + '/'
    if domain: morsel['domain'] = domain
    if secure: morsel['secure'] = secure
    value = morsel.OutputString()
    if httponly: value += '; httponly'
    header('Set-Cookie', value)


def decode_cookie(value):
    try:
        return unicode(value, 'us-ascii')
    except UnicodeError:
        try:
            return unicode(value, 'utf-8')
        except UnicodeError:
            return unicode(value, 'iso8859', 'ignore')


def parse_cookies(http_cookie):
    if '"' in http_cookie:
        cookie = Cookie.SimpleCookie()
        try:
            cookie.load(http_cookie)
        except Cookie.CookieError:
            cookie = Cookie.SimpleCookie()
            for attr_value in http_cookie.split(';'):
                try:
                    cookie.load(attr_value)
                except Cookie.CookieError:
                    pass
        cookies = dict([(k, urllib.unquote(v.value)) for k, v in cookie.iteritems()])
    else:
        cookies = {}
        for key_value in http_cookie.split(';'):
            key_value = key_value.split('=', 1)
            if len(key_value) == 2:
                key, value = key_value
                cookies[key.strip()] = urllib.unquote(value.strip())
    return cookies


def cookies(*requireds, **defaults):
    if defaults.get("_unicode") is True:
        defaults['_unicode'] = decode_cookie

    if '_parsed_cookies' not in request:
        http_cookie = request.env.get("HTTP_COOKIE", "")
        request._parsed_cookies = parse_cookies(http_cookie)

    try:
        return storify(request._parsed_cookies, *requireds, **defaults)
    except KeyError:
        badrequest()
        raise StopIteration


def debug(*args):
    try:
        out = request.environ['wsgi.errors']
    except:
        out = sys.stderr
    for arg in args: print >> out, pprint.pformat(arg)
    return ''


def _debugwrite(x):
    try:
        out = request.environ['wsgi.errors']
    except:
        out = sys.stderr
    out.write(x)


debug.write = _debugwrite


class Request(threadeddict):
    """
    A `storage` object containing various information about the request:
      
    `environ` (aka `env`)
       : A dictionary containing the standard WSGI environment variables.

    `host`
       : The domain (`Host` header) requested by the user.

    `home`
       : The base path for the application.

    `ip`
       : The IP address of the requester.

    `method`
       : The HTTP method used.

    `path`
       : The path request.
       
    `query`
       : If there are no query arguments, the empty string. Otherwise, a `?` followed
         by the query string.

    `fullpath`
       : The full path requested, including query arguments (`== path + query`).

    ### Response Data

    `status` (default: "200 OK")
       : The status code to be used in the response.

    `headers`
       : A list of 2-tuples to be used in the response.

    `output`
       : A string to be used as the response.
    """

    def header(self, hdr, value, unique=False):
        return header(hdr, value, unique)

    def rawinput(self, method=None):
        return rawinput(method)

    def input(self, *requireds, **defaults):
        return input(*requireds, **defaults)

    def data(self):
        return data()

    def setcookie(self, name, value, expires='', domain=None, secure=False, httponly=False, path=None):
        return setcookie(name, value, expires, domain, secure, httponly, path)

    def decode_cookie(self, value):
        return decode_cookie(value)

    def parse_cookies(self, http_cookie):
        return parse_cookies(http_cookie)

    def cookies(self, *requireds, **defaults):
        return cookies(*requireds, **defaults)

    def _get(self):
        return self.rawinput('GET')

    def _post(self):
        return self.rawinput('POST')

    def getlist(self, key):
        v = self.input(**{key: []})
        return v[key]

    def _session(self):
        return session

    GET = property(_get)
    POST = property(_post)
    REQUEST = property(input)
    session = property(_session)


request = Request()


class Render:
    def __init__(self):
        self._render = None

    def __getattr__(self, name):
        if self._render is None:
            templates = tuple(set((conf.settings.TEMPLATE_DIRS + conf.settings.TEMPLATE_PATH)))
            self._render = template.render(templates)
        return getattr(self._render, name)


render = Render()


def TemplateResponse(filename, mime_type=None, args={}, **kwargs):
    if isinstance(args, dict):
        kwargs = dict(kwargs, **args)
    else:
        raise TypeError, "Args Must a dict"

    template_file = filename or kwargs.pop("template_file", None)
    content_type = mime_type or kwargs.pop("mime_type", None)
    _template = template.frender(template_file)

    if content_type:
        return _template(content_type, **kwargs)
    return _template(**kwargs)


def HttpResponse(content="", mimetype=None):
    content_type = mimetype or conf.settings.DEF_CONTENT_TYPES
    header("Content-type", content_type, unique=True)
    return content


session = None

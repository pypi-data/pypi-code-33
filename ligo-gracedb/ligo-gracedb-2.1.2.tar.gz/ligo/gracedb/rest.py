# -*- coding: utf-8 -*-
# Copyright (C) Brian Moe, Branson Stephens (2015)
#
# This file is part of gracedb
#
# gracedb is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gracedb.  If not, see <http://www.gnu.org/licenses/>.

import six.moves.http_client, socket, ssl
import mimetypes
import urllib
import os
import sys
if os.name == 'posix':
    import pwd
import json
from six.moves.urllib.parse import urlparse, urlencode
from base64 import b64encode
import six
from six.moves import map

from .exceptions import HTTPError
from .version import __version__
from .utils import event_or_superevent, handle_str_or_list_arg, safe_netrc, \
    cleanListInput, get_dt_from_openssl_output, is_expired

DEFAULT_SERVICE_URL = "https://gracedb.ligo.org/api/"

#---------------------------------------------------------------------
# This monkey patch forces TLSv1 if the python version is 2.6.6.
# It was introduced because clients connection from CIT *occasionally*
# try to use SSLv3.  See:
# http://stackoverflow.com/questions/18669457/python-httplib-ssl23-get-server-hellounknown-protocol
#---------------------------------------------------------------------
if sys.hexversion < 0x20709f0:
    wrap_socket_orig = ssl.wrap_socket
    def wrap_socket_patched(sock, keyfile=None, certfile=None,
                            server_side=False, cert_reqs=ssl.CERT_NONE,
                            ssl_version=ssl.PROTOCOL_TLSv1, ca_certs=None,
                            do_handshake_on_connect=True,
                            suppress_ragged_eofs=True):
        return wrap_socket_orig(sock, keyfile, certfile, server_side,
                                cert_reqs, ssl_version, ca_certs,
                                do_handshake_on_connect,
                                suppress_ragged_eofs)
    ssl.wrap_socket = wrap_socket_patched

#-----------------------------------------------------------------
# HTTP/S Proxy classes
# Taken from: http://code.activestate.com/recipes/456195/

class ProxyHTTPConnection(six.moves.http_client.HTTPConnection):

    _ports = {'http' : 80, 'https' : 443}

    def request(self, method, url, body=None, headers={}):
        #request is called before connect, so can interpret url and get
        #real host/port to be used to make CONNECT request to proxy
        o = urlparse(url)
        proto = o.scheme
        port = o.port
        host = o.hostname
        if proto is None:
            raise ValueError("unknown URL type: %s" % url)
        if port is None:
            try:
                port = self._ports[proto]
            except KeyError:
                raise ValueError("unknown protocol for: %s" % url)
        self._real_host = host
        self._real_port = port
        six.moves.http_client.HTTPConnection.request(self, method, url, body, headers)


    def connect(self):
        six.moves.http_client.HTTPConnection.connect(self)
        #send proxy CONNECT request
        self.send("CONNECT %s:%d HTTP/1.0\r\n\r\n" % (self._real_host, self._real_port))
        #expect a HTTP/1.0 200 Connection established
        response = self.response_class(self.sock, strict=self.strict, method=self._method)
        (version, code, message) = response._read_status()
        #probably here we can handle auth requests...
        if code != 200:
            #proxy returned and error, abort connection, and raise exception
            self.close()
            raise socket.error("Proxy connection failed: %d %s" % (code, message.strip()))
        #eat up header block from proxy....
        while True:
            #should not use directly fp probably
            line = response.fp.readline()
            if line == '\r\n': break

class ProxyHTTPSConnection(ProxyHTTPConnection):

    default_port = 443

    def __init__(self, host, port = None, key_file = None, cert_file = None,
        strict = None, context = None):
        ProxyHTTPConnection.__init__(self, host, port)
        self.key_file = key_file
        self.cert_file = cert_file
        self.context = context

    def connect(self):
        ProxyHTTPConnection.connect(self)
        #make the sock ssl-aware
        if sys.hexversion < 0x20709f0:
            ssl = socket.ssl(self.sock, self.key_file, self.cert_file)
            self.sock = six.moves.http_client.FakeSocket(self.sock, ssl)
        else:
            self.sock = self.context.wrap_socket(self.sock)

#-----------------------------------------------------------------
# Generic GSI REST

class GsiRest(object):
    """docstring for GracedbRest"""
    def __init__(self, url=DEFAULT_SERVICE_URL, proxy_host=None,
            proxy_port=3128, cred=None, username=None, password=None,
            force_noauth=False, fail_if_noauth=False):
        """
        url: URL of server API
        proxy_host: proxy host
        proxy_port: proxy port
        cred: a tuple or list of (path_to_cert_file, path_to_key_file) or
              a single path to a combined proxy file (if using an X509
              certificate for authentication)
        username: username for basic auth
        password: password for basic auth
        force_noauth: set to True if you want to skip credential lookup and
                      use this client as an unauthenticated user
        fail_if_noauth: set to True if you want the constructor to fail if
                        no authentication credentials are provided or found

        Authentication details:
        You can:
            1. Provide a path to an X509 certificate and key or a single
               combined proxy file
            2. Provide a username and password
        Or:
            The code will look for a certificate in a default location
                (/tmp/x509up_u%d, where %d is your user ID)
            The code will look for a username and password for the specified
                server in $HOME/.netrc
        """

        # Process service URL
        o = urlparse(url)
        port = o.port
        host = o.hostname
        port = port or 443

        # Store information about credentials and authentication type
        self.credentials = {}
        self.auth_type = None

        # Try to get user-provided credentials, if we aren't forcing
        # no authentication
        if not force_noauth:
            credentials_provided = self._process_credentials(cred,
                username, password)

        # If the user didn't provide credentials in the constructor,
        # we try to look up the credentials
        if not force_noauth and not credentials_provided:
            # Look for X509 certificate and key
            cred = self._find_x509_credentials()
            if cred:
                self.credentials['cert_file'], self.credentials['key_file'] = \
                    cred
                credentials_provided = True
                self.auth_type = 'x509'
            else:
                # Look for basic auth credentials in .netrc file
                try:
                    basic_auth_tuple = safe_netrc().authenticators(host)
                except IOError as e:
                    # IOError = no .netrc file found, pass
                    pass
                else:
                    # If credentials were found for host, set them up!
                    if basic_auth_tuple is not None:
                        self.credentials['username'] = basic_auth_tuple[0]
                        self.credentials['password'] = basic_auth_tuple[2]
                        credentials_provided = True
                        self.auth_type = 'basic'

        if (fail_if_noauth and not force_noauth):
            raise RuntimeError('No authentication credentials found')

        # If we are using basic auth, construct auth header
        if (self.auth_type == 'basic'):
            user_and_pass = b64encode('{username}:{password}'.format(
                username=self.credentials['username'],
                password=self.credentials['password']).encode()) \
                .decode('ascii')
            self.authn_header = {
                'Authorization': 'Basic {0}'.format(user_and_pass),
            }

        # Construct version header
        self.version_header = {'User-Agent': 'gracedb-client/{version}'.format(
            version=__version__)}

        # Set up SSL context and connector
        self.set_up_connector(host, port, proxy_host, proxy_port)

    def set_up_connector(self, host, port, proxy_host, proxy_port):
        # Versions of Python earlier than 2.7.9 don't use SSL Context
        # objects for this purpose, and do not do any server cert verification.
        ssl_context = None
        if sys.hexversion >= 0x20709f0:
            # Use the new method with SSL Context
            # Prepare SSL context
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            if (self.auth_type == 'x509'):
                try:
                    ssl_context.load_cert_chain(self.credentials['cert_file'],
                        self.credentials['key_file'])
                except ssl.SSLError as e:
                    msg = ("\nERROR: Unable to load cert/key pair.\n\nPlease "
                        "run ligo-proxy-init or grid-proxy-init again or make "
                        "sure your robot certificate is readable.\n\n")
                    self.output_and_die(msg)
            # Load and verify certificates
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            ssl_context.check_hostname = True
            # Find the various CA cert bundles stored on the system
            ssl_context.load_default_certs()

            if proxy_host:
                self.connector = lambda: ProxyHTTPSConnection(proxy_host, proxy_port, context=ssl_context)
            else:
                self.connector = lambda: six.moves.http_client.HTTPSConnection(host, port, context=ssl_context)
        else:
            # Using an older version of python. We'll pass in the cert and key files.
            creds = self.credentials if self.auth_type == 'x509' else {}
            if proxy_host:
                self.connector = lambda: ProxyHTTPSConnection(proxy_host, proxy_port,
                    **creds)
            else:
                self.connector = lambda: six.moves.http_client.HTTPSConnection(host, port,
                    **creds)

    def _process_credentials(self, cred, username, password):
        """Process credentials provided in the constructor"""
        credentials_provided = False
        if cred:
            if isinstance(cred, (list, tuple)):
                self.credentials['cert_file'], self.credentials['key_file'] = \
                    cred
            else:
                self.credentials['cert_file'] = cred
                self.credentials['key_file'] = cred
            credentials_provided = True
            self.auth_type = 'x509'
        elif username and password:
            self.credentials['username'] = username
            self.credentials['password'] = password
            credentials_provided = True
            self.auth_type = 'basic'
        elif (username is None) ^ (password is None):
            raise RuntimeError('Must provide both username AND password for '
                'basic auth.')

        return credentials_provided

    def _find_x509_credentials(self):
        """
        Tries to find a user's X509 certificate and key.  Checks environment
        variables first, then expected location for default proxy.
        """
        proxyFile = os.environ.get('X509_USER_PROXY')
        certFile = os.environ.get('X509_USER_CERT')
        keyFile = os.environ.get('X509_USER_KEY')

        if certFile and keyFile:
            return certFile, keyFile

        if proxyFile:
            return proxyFile, proxyFile

        # Try default proxy
        proxyFile = os.path.join('/tmp', "x509up_u%d" % os.getuid())
        if os.path.exists(proxyFile):
            return proxyFile, proxyFile

        # Try default cert/key
        homeDir = os.environ.get('HOME')
        certFile = os.path.join(homeDir, '.globus', 'usercert.pem')
        keyFile = os.path.join(homeDir, '.globus', 'userkey.pem')

        if os.path.exists(certFile) and os.path.exists(keyFile):
            return certFile, keyFile

    def show_credentials(self, print_output=True):
        """Prints auth_type and credential information"""
        output = 'Auth type: {0}\n'.format(self.auth_type)
        output += "\n".join(['{k}: {v}'.format(k=k, v=v) for k,v in
            six.iteritems(self.credentials)])

        if print_output:
            print(output)
        else:
            return output

    def getConnection(self):
        return self.connector()

    # When there is a problem with the SSL connection or cert authentication,
    # either conn.request() or conn.getresponse() will throw an exception.
    # The following two wrappers are intended to catch these exceptions and
    # return an intelligible error message to the user.
    # A wrapper for getting the response:
    def get_response(self, conn):
        try:
            return conn.getresponse()
        except ssl.SSLError as e:

            if (self.auth_type == 'x509'):
                # Check for a valid user proxy cert.
                expired, error = is_expired(self.credentials['cert_file'])
                if expired is not None:
                    if expired:
                        msg = ("\nERROR\n\nYour certificate or proxy has "
                            "expired. Please run ligo-proxy-init or "
                            "grid-proxy-init (as appropriate) to generate a "
                            "fresh one.\n\n")
                    else:
                        msg = ("\nERROR\n\nYour certificate appears valid, "
                            "but there was a problem establishing a secure "
                            "connection: {0}").format(e=str(e))
                else:
                    msg = ("\nERROR\n\nUnable to check certificate expiry "
                        "date: {0}\n\nProblem establishing secure connection: "
                        "{1}\n\n").format(error, str(e))
            else:
                msg = ("\nERROR\n\nProblem establishing secure connection: "
                    "{e}\n\n").format(e=str(e))
            self.output_and_die(msg)

    # A wrapper for making the request.
    def make_request(self, conn, *args, **kwargs):
        try:
            conn.request(*args, **kwargs)
        except ssl.SSLError as e:
            msg = "\nERROR \n\n"
            msg += "Problem establishing secure connection: %s \n\n" % str(e)
            self.output_and_die(msg)

    def request(self, method, url, body=None, headers=None, priming_url=None):
        # Bug in Python (versions < 2.7.1 (?))
        # http://bugs.python.org/issue11898
        # if the URL is unicode and the body of a request is binary,
        # the POST/PUT action fails because it tries to concatenate
        # the two which fails due to encoding problems.
        # Workaround is to cast all URLs to str.
        # This is probably bad in general,
        # but for our purposes, today, this will do.
        url = url and str(url)
        priming_url = priming_url and str(priming_url)
        headers = headers or {}
        conn = self.getConnection()

        # Add version string to user-agent header
        headers.update(self.version_header)

        # Add auth header for basic auth
        if (self.auth_type == 'basic'):
            headers.update(self.authn_header)

        # Set up priming URL for certain requests using X509 auth
        if (self.auth_type == 'x509' and priming_url):
            priming_header = {'connection': 'keep-alive'}
            priming_header.update(self.version_header)
            self.make_request(conn, "GET", priming_url, headers=priming_header)
            response = self.get_response(conn)
            if response.status != 200:
                response = self.adjustResponse(response)
            else:
                # Throw away the response and make sure to read the body.
                response = response.read()

        self.make_request(conn, method, url, body, headers or {})
        response = self.get_response(conn)

        # Special handling of 401 unauthorized response for basic auth
        # to catch expired passwords
        if (self.auth_type == 'basic' and response.status == 401):
            try:
                msg = "\nERROR: {e}\n\n".format(json.loads(
                    response.read())['detail'])
            except Exception as e:
                msg = "\nERROR:\n\n"
            msg += ("\nERROR:\n\nPlease check the username/password in your "
                ".netrc file. If your password is more than a year old, you "
                "will need to use the web interface to generate a new one.\n\n")
            self.output_and_die(msg)
        return self.adjustResponse(response)

    def adjustResponse(self, response):
#       XXX WRONG.
        if response.status >= 400:
            response_content = response.read()
            if response.getheader('x-throttle-wait-seconds', None):
                try:
                    rdict = json.loads(response_content)
                    rdict['retry-after'] = response.getheader('x-throttle-wait-seconds')
                    response_content = json.dumps(rdict)
                except:
                    pass
            raise HTTPError(response.status, response.reason, response_content)
        response.json = lambda: self.load_json_or_die(response)
        return response

    def get(self, url, headers=None):
        return self.request("GET", url, headers=headers)

    def head(self, url, headers=None):
        return self.request("HEAD", url, headers=headers)

    def delete(self, url, headers=None):
        return self.request("DELETE", url, headers=headers)

    def options(self, url, headers=None):
        return self.request("OPTIONS", url, headers=headers)

    def post(self, *args, **kwargs):
        return self.post_or_put_or_patch("POST", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.post_or_put_or_patch("PUT", *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.post_or_put_or_patch("PATCH", *args, **kwargs)

    def post_or_put_or_patch(self, method, url, body=None, headers=None,
        files=None):
        headers = headers or {}
        if not files:
            # Simple urlencoded body
            if isinstance(body, dict):
            # XXX What about the headers in the params?
                if 'content-type' not in headers:
                    headers['content-type'] = "application/json"
                body = json.dumps(body)
        else:
            body = body or {}
            if isinstance(body, dict):
                body = list(body.items())
            content_type, body = encode_multipart_formdata(body, files)
            # XXX What about the headers in the params?
            headers = {
                'content-type': content_type,
                'content-length': str(len(body)),
                #'connection': 'keep-alive',
            }
        return self.request(method, url, body, headers)

    # A utility for writing out an error message to the user and then stopping
    # execution. This seems to behave sensibly in both the interpreter and in
    # a script.
    @classmethod
    def output_and_die(cls, msg):
        raise RuntimeError(msg)

    # Given an HTTPResponse object, try to read its content and interpret as
    # JSON--or die trying.
    @classmethod
    def load_json_or_die(cls, response):

        # First check that the response object actually exists.
        if not response:
            raise ValueError("No response object")

        # Next, try to read the content of the response.
        response_content = response.read()
        response_content = response_content.decode('utf-8')
        if not response_content:
            response_content = '{}'

        # Finally, try to create a dict by decoding the response as JSON.
        rdict = None
        try:
            rdict = json.loads(response_content)
        except ValueError:
            msg = "ERROR: got unexpected content from the server:\n"
            msg += response_content
            raise ValueError(msg)

        return rdict

#------------------------------------------------------------------
# GraceDB
#
# Example Gracedb REST client.

class GraceDb(GsiRest):
    """Example GraceDb REST client

    The GraceDB service URL may be passed to the constructor
    if an alternate GraceDb instance is desired:

        >>> g = GraceDb("https://alternate.gracedb.edu/api/")
        >>> r = g.ping()

    The proxy_host and proxy_port may also be passed in if accessing
    GraceDB behind a proxy. For other kwargs accepted by the constructor,
    consult the source code.
    """
    def __init__(self, service_url=DEFAULT_SERVICE_URL, proxy_host=None,
            proxy_port=3128, api_version=None, *args, **kwargs):
        super(GraceDb, self).__init__(service_url, proxy_host,
            proxy_port, *args, **kwargs)

        # Check version type
        if api_version is not None and not isinstance(api_version,
            six.string_types):
            raise TypeError('api_version should be a string')

        # Sets default and versioned service URLs
        # (self._service_url, self._versioned_service_url)
        self._set_service_url(service_url, api_version)

        # Set version
        self._api_version = api_version

        # Set service_info to None, will be obtained from the server when
        # the user takes an action which needs this information.
        self._service_info = None

    def _set_service_url(self, service_url, api_version):
        """Sets versioned and unversioned service URLs"""
        # Make sure path ends with '/'
        if not service_url.endswith('/'):
            service_url += '/'

        # Default service url (unversioned)
        self._service_url = service_url

        # Versioned service url (if version provided)
        self._versioned_service_url = service_url
        if api_version and api_version != 'default':
            # If api_version is 'default', that is equivalent to not setting
            # the version and indicates that the user wants to use the
            # default/non-versioned API
            self._versioned_service_url += (api_version + '/')

    @property
    def service_url(self):
        # Will be removed in the future
        print("DEPRECATED: this attribute has been moved to '_service_url'")
        return self._service_url

    @property
    def service_info(self):
        """Info from root of API. Should be a dict"""
        if not self._service_info:
            # try-except block takes user-specified API version to use and
            # checks whether that version is available on the server
            try:
                r = self.request("GET", self._versioned_service_url)
            except HTTPError as e:
                # If we get a 404 error, that means that the versioned
                # service URL was not found. We assume that this happened
                # because the user requested an unavailable API version.
                if (e.status == 404):
                    # Get versions from unversioned API root
                    r = self.request("GET", self._service_url)
                    available_api_versions = r.json().get('API_VERSIONS', None)
                    if available_api_versions:
                        err_msg = ('Bad API version. Available versions for '
                            'this server are: {0}').format(
                            available_api_versions)
                    else:
                        # Case where server doesn't have versions, for some
                        # reason.
                        err_msg = ('This server does not have a versioned API.'
                            ' Reinstantiate your client without a version.')

                    # Raise error
                    raise ValueError(err_msg)
                else:
                    # Not a 404 error, must be something else
                    raise e
            else:
                if r.status != 200:
                    raise HTTPError(r.status, r.reason, r.read())
            self._service_info = r.json()
        return self._service_info

    @property
    def api_versions(self):
        return self.service_info.get('API_VERSIONS')

    @property
    def links(self):
        return self.service_info.get('links')

    @property
    def templates(self):
        return self.service_info.get('templates')

    @property
    def groups(self):
        return self.service_info.get('groups')

    @property
    def pipelines(self):
        return self.service_info.get('pipelines')

    @property
    def searches(self):
        return self.service_info.get('searches')

    # Would like to call this 'labels' to keep in line with how
    # other properties are named, but it's already used for a function.
    @property
    def allowed_labels(self):
        return self.service_info.get('labels')

    @property
    def em_groups(self):
        return self.service_info.get('em-groups')

    @property
    def wavebands(self):
        return self.service_info.get('wavebands')

    @property
    def eel_statuses(self):
        return self.service_info.get('eel-statuses')

    @property
    def obs_statuses(self):
        return self.service_info.get('obs-statuses')

    @property
    def voevent_types(self):
        return self.service_info.get('voevent-types')

    @property
    def superevent_categories(self):
        return self.service_info.get('superevent-categories')

    @property
    def instruments(self):
        return self.service_info.get('instruments')

    @property
    def signoff_types(self):
        return self.service_info.get('signoff-types')

    @property
    def signoff_statuses(self):
        return self.service_info.get('signoff-statuses')

    def request(self, method, url, body=None, headers=None, priming_url=None):
        if (method.upper() in ['POST', 'PUT'] and self.auth_type == 'x509'):
            priming_url = self._service_url
        return super(GraceDb, self).request(method, url, body, headers,
            priming_url)

    def _getCode(self, input_value, code_dict):
        """
        Check if input is valid and return coded version if it is
        code_dict is dict of { code : descriptive_name }
        """
        # Quick check for simple case where it's already coded
        if input_value in code_dict:
            return input_value

        # Loop over code_dict items, if we match either the key or
        # value (case-insensitive), return the code.
        input_lower = input_value.lower()
        for code, display in six.iteritems(code_dict):
            if (input_lower == code.lower() or
                input_lower == display.lower()):
                return code

        # Not found, return None
        return None

    # Search and filecontents are optional when creating an event.
    def createEvent(self, group, pipeline, filename, search=None, labels=None,
                    offline=False, filecontents=None, **kwargs):
        """Create a new GraceDB event

        Required args: group, pipeline, filename

        Optional args: search, labels, offline, filecontents

        The filename is the path to a file containing information about the
        event. The values for 'group', 'pipeline', and 'search' are restricted
        to those stored in the database. 'labels' should be a list of strings
        corresponding to labels (values restricted to those stored in the
        database).  'labels' can be a string if only a single label is
        being applied. 'offline' is a boolean which indicates whether the
        analysis is offline (True) or online/low-latency (False).

        Example:

            >>> g = GraceDb()
            >>> r = g.createEvent('CBC', 'gstlal', '/path/to/something.xml',
            ... labels='INJ', 'LowMass')
            >>> r.status
            201

        """
        errors = []
        if group not in self.groups:
            errors += ["bad group"]
        if pipeline not in self.pipelines:
            errors += ["bad pipeline"]
        if search and search not in self.searches:
            errors += ["bad search"]
        # Process offline arg
        if not isinstance(offline, bool):
            errors += ["offline should be True or False"]
        # Process label args - convert non-empty strings to list
        # to ensure consistent processing
        if labels:
            if isinstance(labels, six.string_types):
                # Convert to list
                labels = [labels]
            elif isinstance(labels, list):
                pass
            else:
                # Raise exception instead of adding errors. The next for loop
                # will break (before errors exception is raised) if labels
                # is of the wrong type
                raise TypeError("labels arg is {0}, should be str or list" \
                    .format(type(labels)))
            # Check labels against those in database
            for l in labels:
                if l not in self.allowed_labels:
                    raise NameError(("Label '{0}' does not exist in the "
                        "database").format(l))
        if errors:
            # XXX Terrible error messages / weak exception type
            raise Exception(str(errors))
        if filecontents is None:
            if filename == '-':
                filename = 'initial.data'
                filecontents = sys.stdin.read()
            else:
                filecontents = open(filename, 'rb').read()

        fields = [
            ('group', group),
            ('pipeline', pipeline),
            ('offline', offline),
        ]
        if search:
            fields.append(('search', search))
        if labels:
            for l in labels:
                fields.append(('labels', l))

        # Update fields with additional keyword arguments
        for key, value in six.iteritems(kwargs):
            fields.append((key, value))

        files = [('eventFile', filename, filecontents)]
        # Python httplib bug?  unicode link
        uri = str(self.links['events'])
        return self.post(uri, fields, files=files)

    def replaceEvent(self, graceid, filename, filecontents=None):
        """Replace an existing GraceDB event

        Required args: graceid, filename

        This function uploads a new event file, hence changing the basic details
        of an existing event.

        Example:

            >>> g = GraceDb()
            >>> r = g.replaceEvent('T101383', '/path/to/new/something.xml')

        """
        if filecontents is None:
            # Note: not allowing filename '-' here.  We want the event datafile
            # to be versioned.
            filecontents = open(filename, 'rb').read()
        return self.put(
                self.templates['event-detail-template'].format(graceid=graceid),
                files=[('eventFile', filename, filecontents)])

    def event(self, graceid):
        """Get information about a specific event

        Args: graceid

        Example:

            >>> g = GraceDb()
            >>> event_dict = g.event('T101383').json()

        """
        return self.get(
                self.templates['event-detail-template'].format(graceid=graceid))

    def events(self, query=None, orderby=None, count=None, columns=None,
        max_results=None):
        """Get a iterator of events in response to a query

        This function returns an iterator which yields event dictionaries.
        Optional arguments are query, orderby, count, and columns. The
        columns argument is a comma separated list of attributes that the
        user would like in each event dictionary. If columns are not specified,
        all attributes of the events are returned.

        Example:

            >>> g = GraceDb()
            >>> for event in g.events('ER5 submitter: "gstlalcbc"', columns='graceid,far,gpstime'):
            ...     print "%s %e %d" % (event['graceid'], event['far'], event['gpstime'])


        """
        uri = self.links['events']
        qdict = {}
        if query:   qdict['query'] = query
        if count is not None:   qdict['count'] = count
        if orderby: qdict['sort'] = orderby
        if columns: qdict['columns'] = columns
        if qdict:
            uri += "?" + urlencode(qdict)
        n = 0
        while uri:
            response = self.get(uri).json()
            events = response.get('events',[])
            uri = response.get('links',{}).get('next')

            for event in events:
                n += 1
                if (max_results is not None and n > max_results):
                    break
                yield event

    def numEvents(self, query=None):
        """Get the number of events satisfying a query

        Example:

            >>> g = GraceDb()
            >>> g.numEvents('ER5 submitter: "gstlalcbc"')
            213

        """
        uri = self.links['events']
        if query:
            uri += "?" + urlencode({'query': query})
        return self.get(uri).json()['numRows']

    def createSuperevent(self, t_start, t_0, t_end, preferred_event,
        category='production', events=[], labels=None):
        """
        Create a superevent.

        Signature:
        createSuperevent(t_start, t_0, t_end, preferred_event,
            events=[], labels=None)

        Arguments:
            t_start:         t_start of superevent
            t_0:             t_0 of superevent
            t_end:           t_end of superevent
            preferred_event: graceid corresponding to event which will be set
                             as the preferred event for this superevent
            category:        superevent category ('production', 'test', 'mdc')
            events:          list of graceids corresponding to events which
                             should be attached to this superevent (optional)
            labels:          list of labels which should be attached to this
                             superevent at creation (optional)

        Example:

            >>> g = GraceDb()
            >>> r = g.createSuperevent(1, 2, 3, 'G123456',
            ... category='production', events=['G100', 'G101'],
            ... labels=['EM_READY', 'DQV'])
            >>> r.status
            201
        """
        # Process label args - convert non-empty strings to list
        # to ensure consistent processing
        if labels:
            if isinstance(labels, six.string_types):
                labels = [labels]
            elif isinstance(labels, list):
                pass
            else:
                raise TypeError("labels arg is {0}, should be str or list" \
                    .format(type(labels)))
            # Check labels against those in database
            for l in labels:
                if l not in self.allowed_labels:
                    raise NameError(("Label '{0}' does not exist in the "
                        "database").format(l))
        if events:
            if isinstance(events, six.string_types):
                events = [events]
            elif isinstance(events, list):
                pass
            else:
                raise TypeError("events arg is {0}, should be str or list" \
                    .format(type(events)))

        # validate category, convert to short form if necessary
        category = self._getCode(category.lower(),
            self.superevent_categories)
        if not category:
            raise ValueError("category must be one of: {0}".format(
                list(six.itervalues(self.superevent_categories))))

        # Set up request body for POST
        request_body = {
            't_start': t_start,
            't_0': t_0,
            't_end': t_end,
            'preferred_event': preferred_event,
            'category': category,
        }
        if events:
            request_body['events'] = events
        if labels:
            request_body['labels'] = labels

        # Python httplib bug?  unicode link
        uri = self.links['superevents']
        return self.post(uri, body=request_body)

    def updateSuperevent(self, superevent_id, t_start=None, t_0=None,
        t_end=None, preferred_event=None):
        """
        Update a superevent's parameters.

        Signature:
        updateSuperevent(superevent_id, t_start=None, t_0=None,
            t_end=None, preferred_event=None)

        Arguments:
            superevent_id:   id of superevent to update
            t_start:         t_start of superevent
            t_0:             t_0 of superevent
            t_end:           t_end of superevent
            preferred_event: graceid corresponding to event which will be set
                             as the preferred event for this superevent

            Any combination of these parameters (other than superevent_id)
            may be used; none are required.

        Example:

            >>> g = GraceDb()
            >>> r = g.updateSuperevent('S0001', t_start=12, preferred_event=
            ... 'G654321')
            >>> r.status
            200
        """
        # Make sure that at least one parameter is provided
        if not (t_start or t_0 or t_end or preferred_event):
            raise ValueError('Provide at least one of t_start, t_0, t_end, or '
                'preferred_event')

        request_body = {}
        if t_start is not None:
            request_body['t_start'] = t_start
        if t_0 is not None:
            request_body['t_0'] = t_0
        if t_end is not None:
            request_body['t_end'] = t_end
        if preferred_event is not None:
            request_body['preferred_event'] = preferred_event
        template = self.templates['superevent-detail-template']
        uri = template.format(superevent_id=superevent_id)
        return self.patch(uri, body=request_body)

    def addEventToSuperevent(self, superevent_id, graceid):
        """
        Add an event to a superevent. Events can only be part of one superevent
        so the server will throw an error if the event is part of another
        superevent already.

        Signature:
            addEventToSuperevent(superevent_id, graceid)

        Arguments:
            superevent_id: id of superevent to which the event will be added
            graceid:       graceid of event to add to superevent

        Example:

            >>> g = GraceDb()
            >>> r = addEventToSuperevent('S0001', 'G123456')
            >>> r.status
            201
        """
        request_body = {'event': graceid}
        template = self.templates['superevent-event-list-template']
        uri = template.format(superevent_id=superevent_id)
        return self.post(uri, body=request_body)

    def removeEventFromSuperevent(self, superevent_id, graceid):
        """
        Remove an event from a superevent.

        Signature:
            removeEventFromSuperevent(superevent_id, graceid)

        Arguments:
            superevent_id, graceid

        Example:

            >>> g = GraceDb()
            >>> r = removeEventFromSuperevent('S0001', 'G123456')
            >>> r.status
            204
        """
        template = self.templates['superevent-event-detail-template']
        uri = template.format(superevent_id=superevent_id, graceid=graceid)
        return self.delete(uri)

    def superevent(self, superevent_id):
        """
        Get information about a specific superevent.

        Signature:
            superevent(superevent_id)

        Arguments:
            superevent_id

        Example:

            >>> g = GraceDb()
            >>> superevent = g.superevent('S0001').json()
        """
        return self.get(self.templates['superevent-detail-template'].format(
            superevent_id=superevent_id))

    def superevents(self, query='', orderby=[], count=None, columns=[],
        max_results=None):
        """
        Get an iterator of superevents in response to a query.

        Signature:
            superevents(query='', orderby=[], count=None, columns=[])

        Arguments:
            query: query string for filtering superevents (same as on the
                   web interface)
            orderby: list of strings corresponding to attribute(s) of the
                     superevents used to order the results (optional).
                     Available options: created, t_start, t_0, t_end, is_gw,
                     id, preferred_event. Default is ascending order, but
                     prefix any option with "-" to apply descending order.
            count: each generator iteration will yield this many objects
                   (optional; default determined by the server)
            columns: which attributes of the superevents to return
                     (default: all).

        Example:

            >>> g = GraceDb()
            >>> for s in g.superevents(query='is_gw=True', orderby=['-preferred_event'], columns='superevent_id,events'):
            ...     print(s['superevent_id'])
        """
        # If columns is a comma-separated string, split it to a list
        if isinstance(columns, six.string_types):
            columns = columns.split(',')

        # If orderby is a list (should be), convert it to a comma-separated
        # string (that's what the server expects)
        if isinstance(orderby, list):
            orderby = ",".join(orderby)

        # Get URI
        uri = self.links['superevents']

        # Compile URL parameters
        qdict = {}
        if query:   qdict['query'] = query
        if count is not None:   qdict['count'] = count
        if orderby: qdict['sort'] = orderby
        if qdict:
            uri += "?" + urlencode(qdict)

        # Get superevent information and construct a generator
        n = 0
        while uri:
            response = self.get(uri).json()
            superevents = response.get('superevents',[])
            uri = response.get('links',{}).get('next')

            for superevent in superevents:
                n += 1
                if (max_results is not None and n > max_results):
                    break
                # If columns are specified, only return specific values
                if columns:
                    yield {k: superevent[k] for k in columns}
                else:
                    yield superevent

    def confirm_superevent_as_gw(self, superevent_id):
        """
        Upgrade a superevent's state to 'confirmed GW'.
        Requires specific server-side permissions.

        Signature:
            confirm_superevent_as_gw(superevent_id)

        Arguments:
            superevent_id
        """
        template = self.templates['superevent-confirm-as-gw-template']
        uri = template.format(superevent_id=superevent_id)
        return self.post(uri)

    @event_or_superevent
    def files(self, object_id, filename="", *args, **kwargs):
        """
        Files for a particular event or superevent.

        Signature:
            files(object_id, filename="")

        Arguments:
            object_id: event graceid or superevent id
            filename:  name of file (optional)

        If a filename is not specified, a list of filenames associated with the
        event or superevent is returned.
        If a filename is specified, the file's content is returned.

        Example 1: get a list of files

            >>> g = GraceDb()
            >>> event_files = g.files('T101383').json()
            >>> for filename in event_files.keys():
            ...     # do something
            ...     pass

        Example 2: get a file's content

            >>> outfile = open('my_skymap.png', 'w')
            >>> r = g.files('T101383', 'skymap.png')
            >>> outfile.write(r.read())
            >>> outfile.close()

        """
        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            uri_kwargs = {'superevent_id': object_id}
            if filename:
                # Get specific file
                uri_kwargs['file_name'] = filename
                template = self.templates['superevent-file-detail-template']
            else:
                # Get list of files
                template = self.templates['superevent-file-list-template']
        else:
            template = self.templates['files-template']
            uri_kwargs = {'graceid': object_id, 'filename': filename}
        uri = template.format(**uri_kwargs)
        return self.get(uri)

    def writeFile(self, object_id, filename, filecontents=None):
        """
        Upload a file for an event or superevent.

        Signature:
            writeFile(object_id, filename, filecontents=None)

        Required args:
            object_id: event graceid or superevent id
            filename:  path to file

        This method creates a new log message with your file attached. It is
        strongly preferred to use writeLog() instead of writeFile() so that you
        can add a more suitable comment. That will make it easier for other
        users to know what your file contains.

        Example:

            >>> g = GraceDb()
            >>> r = g.writeFile('T101383', '/path/to/my_interesting_plot.png')
            >>> print r.status

        """
        print("WARNING: the writeFile() method is deprecated in favor "
            "of writeLog() and will be removed in a future release.")
        return self.writeLog(object_id, "FILE UPLOAD", filename, filecontents)

    @event_or_superevent
    def logs(self, object_id, log_number=None, *args, **kwargs):
        """
        Get log messages associated with an event or superevent

        Signature:
            logs(object_id, log_number=None)

        Arguments:
            object_id:  event graceid or superevent id
            log_number: log message number (N) of log message to retrieve
                        (optional)

        If a log_number is specified, only a single log message is returned.
        If a log_number is not specified, a list of all log messages attached
        to the event or superevent in questions is returned.

        Example 1: get all log messages

            >>> g = GraceDb()
            >>> response_dict = g.logs('T101383').json()
            >>> print "Num logs = %d" % response_dict['numRows']
            >>> log_list = response_dict['log']
            >>> for log in log_list:
            ...     print log['comment']

        Example 2: get a single log message

            >>> g = GraceDb()
            >>> log_info = g.logs('T101383', 10).json()
        """
        if log_number is not None and not isinstance(log_number, int):
            raise TypeError('log_number should be an int')

        # Set up template and object id
        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            uri_kwargs = {'superevent_id': object_id}
            if log_number:
                template = self.templates['superevent-log-detail-template']
            else:
                template = self.templates['superevent-log-list-template']
        else:
            uri_kwargs = {'graceid': object_id}
            if log_number:
                template = self.templates['event-log-detail-template']
            else:
                template = self.templates['event-log-template']

        if log_number is not None:
            uri_kwargs['N'] = log_number

        uri = template.format(**uri_kwargs)
        return self.get(uri)

    @event_or_superevent
    def writeLog(self, object_id, message, filename=None, filecontents=None,
            tag_name=[], displayName=[], *args, **kwargs):
        """
        Create a new log message.

        Signature:
        writeLog(object_id, message, filename=None, filecontents=None,
            tag_name=[], displayName=[])

        Arguments:
            object_id:    event graceid or superevent id
            message:      comment to post on the event log
            filename:     path to file to be uploaded (optional)
            filecontents: handler pointing to a file to be read
                          (optional)
            tag_name:     tag name string or list of tag names to be attached
                          to the log message
            displayName:  tag display name string or list of display names for
                          tags. If provided, there should be one for each tag.
                          (optional)

        If only object_id and message are provided, a text comment will be
        created in the event or superevent log. If a filename is also
        specified, the file will be attached to the log message and displayed
        alongside the message text. If a tag_name is provided, the message will
        be tagged.

        Example:

            >>> g = GraceDb()
            >>> r = g.writeLog('T101383', 'Good stuff.', '/path/to/plot.png',
            ... tag_name='analyst_comments')
            >>> print r.status
            201
        """
        # Check displayName length - should be 0 or same as tag_name
        if displayName and isinstance(tag_name, list) and \
            len(displayName) != len(tag_name):
            raise ValueError("For a list of tags, either provide no display "
                "names or a display name for each tag")

        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            template = self.templates['superevent-log-list-template']
            uri_kwargs = {'superevent_id': object_id}
        else:
            template = self.templates['event-log-template']
            uri_kwargs = {'graceid': object_id}
        uri = template.format(**uri_kwargs)
        files = None
        if filename:
            if filecontents is None:
                if filename == '-':
                    filename = 'stdin'
                    filecontents = sys.stdin.read()
                else:
                    filecontents = open(filename, "rb").read()
            elif hasattr(filecontents, 'read'):
                # XXX Does not scale well.
                filecontents = filecontents.read()
            files = [('upload', os.path.basename(filename), filecontents)]

        # Handle cases where tag_name or displayName are strings
        if isinstance(tag_name, str):
            tag_name = [tag_name]
        elif isinstance(tag_name, (tuple, set)):
            tag_name = list(tag_name)
        elif tag_name is None:
            tag_name = []

        if isinstance(displayName, str):
            displayName = [displayName]
        elif isinstance(displayName, (tuple, set)):
            displayName = list(displayName)
        elif displayName is None:
            displayName = []

        # Set up body of request
        body = {
            'comment': message,
            'tagname': tag_name,
            'displayName': displayName,
        }

        # If files are attached, we have to encode the request body
        # differently, so we convert from a dict to a list of tuples.
        if files:
            fields = []
            for k,v in body.items():
                if isinstance(v, list):
                    for item in v: fields.append((k, item))
                else:
                    fields.append((k,v))
            body = fields

        return self.post(uri, body, files=files)

    def eels(self, graceid):
        """Given a GraceID, get a list of EMBB log entries

        Example:

            >>> g = GraceDb()
            >>> r = g.eels('T101383')
            >>> full_dictionary = r.json()            # Convert the response to a dictionary
            >>> eel_list = full_dictionary['embblog'] # Pull out a list of EEL dicts

        """

        template = self.templates['embb-event-log-template']
        uri = template.format(graceid=graceid)
        return self.get(uri)

    def writeEel(self, graceid, group, waveband, eel_status,
            obs_status, **kwargs):
        """Write an EMBB event log entry

        Required args: graceid, group, waveband, eel_status, obs_status

        (Note that 'group' here is the name of the EM MOU group, not
        the LVC data analysis group responsible for the original detection.)

        Additional keyword arguments may be passed in to be sent in the POST
        data. Only the following kwargs are recognized:
            ra
            dec
            raWidth
            decWidth
            gpstime
            duration
            comment
            extra_info_dict

        Most of these are self-explanatory, but the 'extra_info_dict' is meant
        to be a JSON string containing any additional information the user may
        wish to convey.

        Any other kwargs will be ignored.
        """
        # validate facility, waveband, eel_status, and obs_status
        if not group in self.em_groups:
            raise ValueError("group must be one of %s" % self.em_groups)

        if not waveband in list(self.wavebands.keys()):
            raise ValueError("waveband must be one of %s" % list(self.wavebands.keys()))

        eel_status = self._getCode(eel_status, self.eel_statuses)
        if not eel_status:
            raise ValueError("EEL status must be one of %s" % list(self.eel_statuses.values()))

        obs_status = self._getCode(obs_status, self.obs_statuses)
        if not obs_status:
            raise ValueError("Observation status must be one of %s" % list(self.obs_statuses.values()))

        template = self.templates['embb-event-log-template']
        uri = template.format(graceid=graceid)

        body = {
            'group' : group,
            'waveband' : waveband,
            'eel_status' : eel_status,
            'obs_status' : obs_status,
        }
        body.update(**kwargs)
        return self.post(uri, body=body)

    @event_or_superevent
    def emobservations(self, object_id, emobservation_num=None, *args,
        **kwargs):
        """
        Given an event graceid or superevent id, get a list of EM observation
        entries or a specific EM observation.

        Signature:
            emobservations(object_id, emobservation_num=None)

        Arguments:
            object_id: event graceid or superevent id
            emobservation_num: number of the EM observation (N) (optional)

        Example 1: get a list of EM observations

            >>> g = GraceDb()
            >>> r = g.emobservations('T101383')
            >>> full_dictionary = r.json()
            >>> emo_list = full_dictionary['observations']

        Example 2: get a single EM observation

            >>> g = GraceDb()
            >>> r = g.emobservations('T101383', 2)
            >>> observation_dict = r.json()
        """
        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            uri_kwargs = {'superevent_id': object_id}
            if emobservation_num:
                template = self.templates['superevent-emobservation-detail-template']
            else:
                template = self.templates['superevent-emobservation-list-template']
        else:
            uri_kwargs = {'graceid': object_id}
            if emobservation_num:
                template = self.templates['emobservation-detail-template']
            else:
                template = self.templates['emobservation-list-template']

        if emobservation_num is not None:
            uri_kwargs['N'] = emobservation_num

        uri = template.format(**uri_kwargs)
        return self.get(uri)

    @event_or_superevent
    def writeEMObservation(self, object_id, group, raList, raWidthList,
        decList, decWidthList, startTimeList, durationList, comment="",
        *args, **kwargs):
        """
        Write an EM observation entry.

        Signature:
            writeEMObservation(object_id, group, raList, raWidthList,
                decList, decWidthList, startTimeList, durationList,
                comment=None)

        Arguments:
            object_id: event graceid or superevent id
            group: name of EM MOU group making the observation
            raList: list of right ascensions (deg.)
            raWidthList: list of right ascension widths OR a single number
                         if all measurements have the same width (deg.)
            decList: list of declinations (deg.)
            decWidthList: list of declination widths OR a single number
                          if all measurements have the same width (deg.)
            startTimeList: list of measurement start times (ISO 8601 UTC)
                           format example: 2018-05-25T16:30:12+00:00
            durationList: list of exposure times OR a single number if all
                          measurements have the same exposure (seconds)
            comment: comment on observation (optional)
        """
        # validate facility, waveband, eel_status, and obs_status
        if not group in self.em_groups:
            raise ValueError("group must be one of %s" % self.em_groups)

        # Argument checking
        num_measurements = len(raList)
        # convert any single number widths or durations into lists
        raWidthList, decWidthList, durationList = \
            [[l] * num_measurements if not isinstance(l, (list, tuple)) else l
            for l in [raWidthList, decWidthList, durationList]]

        # Compare all list lengths
        all_lists = [raList, decList, startTimeList, raWidthList,
            decWidthList, durationList]
        if not all(map(lambda l: len(l) == num_measurements, all_lists)):
            raise ValueError('raList, decList, startTimeList, raWidthList, '
                'decWidthList, and durationList should be the same length')

        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            template = self.templates['superevent-emobservation-list-template']
            uri_kwargs = {'superevent_id': object_id}
        else:
            template = self.templates['emobservation-list-template']
            uri_kwargs = {'graceid': object_id}
        uri = template.format(**uri_kwargs)

        body = {
            'group' : group,
            'ra_list' : raList,
            'ra_width_list': raWidthList,
            'dec_list' : decList,
            'dec_width_list': decWidthList,
            'start_time_list': startTimeList,
            'duration_list': durationList,
            'comment': comment,
        }
        return self.post(uri, body=body)

    @event_or_superevent
    def labels(self, object_id, label="", *args, **kwargs):
        """
        Get a list of labels or a single label for an event or superevent.

        Signature:
            labels(object_id, label="")

        Arguments:
            object_id: event graceid or superevent id
            label:     name of label (optional)

        Example 1: get list of labels

            >>> g = GraceDb()
            >>> label_list = g.labels('T101383').json()['labels']
            >>> for label in label_list:
            ...     print label['name']

        Example 2: get a single label

            >>> g = GraceDb()
            >>> dqv_label = g.labels('T101383', 'DQV').json()

        """
        # Check label name
        if label and label not in self.allowed_labels:
            raise NameError(("Label '{0}' does not exist in the "
                "database").format(label))

        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            uri_kwargs = {'superevent_id': object_id}
            if label:
                template = self.templates['superevent-label-detail-template']
                uri_kwargs['label_name'] = label
            else:
                template = self.templates['superevent-label-list-template']
        else:
            template = self.templates['event-label-template']
            uri_kwargs = {'graceid': object_id}
            uri_kwargs['label'] = label

        uri = template.format(**uri_kwargs)
        return self.get(uri)

    @event_or_superevent
    def writeLabel(self, object_id, label, *args, **kwargs):
        """
        Add a new label to an event or superevent.

        Signature:
            writeLabel(object_id, label)

        Arguments:
            object_id: event graceid or superevent id
            label:     label name

        The label name must correspond to one of the existing
        GraceDB labels (see self.allowed_labels), or an error will result.

        Example:

            >>> g = GraceDb()
            >>> r = g.writeLabel('T101383', 'DQV')
            >>> r.status
            201

        """
        # Check label name
        if label not in self.allowed_labels:
            raise NameError(("Label '{0}' does not exist in the "
                "database").format(label))

        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            template = self.templates['superevent-label-list-template']
            uri_kwargs = {'superevent_id': object_id}
            request_body = {'name': label}
            method = 'POST'
        else:
            template = self.templates['event-label-template']
            uri_kwargs = {'graceid': object_id}
            uri_kwargs['label'] = label
            request_body = {}
            method = 'PUT'
        uri = template.format(**uri_kwargs)
        return self.post_or_put_or_patch(method, uri, body=request_body)

    @event_or_superevent
    def removeLabel(self, object_id, label, *args, **kwargs):
        """
        Remove a label from an event or superevent.

        Signature:
            removeLabel(object_id, label)

        Arguments:
            object_id: event graceid or superevent id
            label:     name of label to be removed

        Example:

            >>> g = GraceDb()
            >>> r = g.removeLabel('T101383', 'DQV')
            >>> r.status
            204
        """
        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            template = self.templates['superevent-label-detail-template']
            uri_kwargs = {'superevent_id': object_id}
            uri_kwargs['label_name'] = label
        else:
            template = self.templates['event-label-template']
            uri_kwargs = {'graceid': object_id}
            uri_kwargs['label'] = label
        uri = template.format(**uri_kwargs)
        return self.delete(uri)

    @event_or_superevent
    def tags(self, object_id, N, *args, **kwargs):
        """
        Get a list of tags associated with a particular event or superevent
        log message.

        Signature:
            tags(object_id, N)

        Arguments:
            object_id: event graceid or superevent id
            N:         log message number

        Example:

            >>> g = GraceDb()
            >>> tag_list = g.tags('T101383', 56).json()['tags']
            >>> print "Number of tags for message 56: %d" % len(tag_list)
        """
        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            uri_kwargs = {'superevent_id': object_id}
            template = self.templates['superevent-log-tag-list-template']
        else:
            uri_kwargs = {'graceid': object_id}
            template = self.templates['taglist-template']
        uri_kwargs['N'] = N
        uri = template.format(**uri_kwargs)
        return self.get(uri)

    def createTag(self, object_id, N, tag_name, displayName=None, *args,
        **kwargs):
        print('WARNING: the createTag() method is deprecated in favor of '
            'addTag() and will be removed in a future release.')
        return self.createTag(object_id, N, tag_name, displayName, *args,
            **kwargs)

    @event_or_superevent
    def addTag(self, object_id, N, tag_name, displayName=None, *args,
        **kwargs):
        """
        Add a new tag to an event or superevent log message.

        Signature:
            addTag(object_id, N, tag_name, displayName=None)

        Arguments:
            object_id:   event graceid or superevent id
            N:           log message number
            tag_name:    name of tag to add; tags which don't exist already
                         will be created.
            displayName: tag display name (optional)

        If a displayName is provided (and if the tag doesn't already exist), a
        new tag will be created with the provided displayName.

        Example:

            >>> g = GraceDb()
            >>> r = g.createTag('T101383', 56, 'sky_loc')
            >>> r.status
            201
        """
        is_superevent = kwargs.pop('is_superevent', False)
        request_body = {}
        if is_superevent:
            template = self.templates['superevent-log-tag-list-template']
            uri_kwargs = {'superevent_id': object_id}
            request_body['name'] = tag_name
            method = 'POST'
        else:
            template = self.templates['tag-template']
            uri_kwargs = {'graceid': object_id, 'tag_name': tag_name}
            method = 'PUT'

        # Add displayName to requestBody, if applicable.
        if displayName is not None:
            request_body['displayName'] = displayName

        uri_kwargs['N'] = N
        uri = template.format(**uri_kwargs)
        return self.post_or_put_or_patch(method, uri, body=request_body)

    def deleteTag(self, object_id, N, tag_name, *args, **kwargs):
        print('WARNING: the deleteTag() method is deprecated in favor of '
            'removeTag() and will be removed in a future release.')
        return self.removeTag(object_id, N, tag_name, *args, **kwargs)

    @event_or_superevent
    def removeTag(self, object_id, N, tag_name, *args, **kwargs):
        """
        Remove a tag from a given event or superevent log message.

        Signature:
            removeTag(object_id, N, tag_name)

        Arguments:
            object_id: event graceid or superevent id
            N:         log message number
            tag_name:  name of the tag to be removed

        Example:

            >>> g = GraceDb()
            >>> r = g.deleteTag('T101383', 56, 'sky_loc')
            >>> r.status
            200
        """
        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            template = self.templates['superevent-log-tag-detail-template']
            uri_kwargs = {'superevent_id': object_id}
        else:
            template = self.templates['tag-template']
            uri_kwargs = {'graceid': object_id}
        uri_kwargs['N'] = N
        uri_kwargs['tag_name'] = tag_name
        uri = template.format(**uri_kwargs)
        return self.delete(uri)

    def ping(self):
        """Ping the server

        If you get back an HTTPResponse object, it's alive.
        The JSON content is the service info, which is normally not of
        interest. But you can use it to get the known Groups, Searches,
        Pipelines, etc.

        Example:

            >>> g = GraceDb()
            >>> groups = g.ping().json()['groups']

        """
        return self.get(self.links['self'])

    @event_or_superevent
    def voevents(self, object_id, voevent_num=None, *args, **kwargs):
        """
        Get a list of VOEvents or a single VOEvent for an event or superevent.

        Signature:
            voevents(object_id, voevent_num=None)

        Arguments:
            object_id:   event graceid or superevent id
            voevent_num: number of VOEvent to retrieve (optional)

        Example 1: get a list of VOEvents

            >>> g = GraceDb()
            >>> r = g.voevents('T101383')
            >>> voevent_list = r.json()['voevents']

        Example 2: get a single VOEvent

            >>> g = GraceDb()
            >>> r = g.voevents('T101383')
            >>> voevent_list = r.json()['voevents']
        """
        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            uri_kwargs = {'superevent_id': object_id}
            if voevent_num:
                template = self.templates['superevent-voevent-detail-template']
            else:
                template = self.templates['superevent-voevent-list-template']
        else:
            uri_kwargs = {'graceid': object_id}
            if voevent_num:
                template = self.templates['voevent-detail-template']
            else:
                template = self.templates['voevent-list-template']

        if voevent_num is not None:
            uri_kwargs['N'] = voevent_num

        uri = template.format(**uri_kwargs)
        return self.get(uri)

    @event_or_superevent
    def createVOEvent(self, object_id, voevent_type, skymap_type=None,
        skymap_filename=None, internal=True, open_alert=False,
        hardware_inj=False, CoincComment=False, ProbHasNS=None,
        ProbHasRemnant=None, BNS=None, NSBH=None, BBH=None, Terrestrial=None,
        *args, **kwargs):
        """Create a new VOEvent

        Signature:
            createVOEvent(self, object_id, voevent_type, skymap_type=None,
                skymap_filename=None, internal=True, open_alert=False,
                hardware_inj=False, CoincComment=False, ProbHasNS=None,
                ProbHasRemnant=None, BNS=None, NSBH=None, BBH=None,
                Terrestrial=None)

        Arguments:
            object_id: event graceid or superevent id
            voevent_type: VOEvent type (options: 'preliminary', 'initial',
                          'update', 'retraction')
            skymap_type: skymap type (required for voevents which include a
                         skymap)
            skymap_filename: name of skymap file in GraceDB (required for
                             'initial' and 'update' alerts, optional for
                             'preliminary' alerts.
            internal: whether the VOEvent should be distributed to LVC members
                      only (True/False)
            hardware_inj: whether the candidate is a hardware injection
                          (True/False)
            open_alert: whether the candidate is an open alert or not
                        (True/False)
            CoincComment: whether the candidate has a possible counterpart
                          GRB (True/False)

        The following arguments are optional and only apply to CBC events:
            ProbHasNS: probability that at least one object in the binary is
                       less than 3 M_sun (optional)
            ProbHasRemnant: probability that there is matter in the
                            surroundings of the central object (optional)
            BNS: probability that the source is a binary neutron star merger
            NSBH: probability that the source is a neutron star-black hole
                  merger
            BBH: probability that the source is a binary black hole merger
            Terrestrial: probability that the source is terrestrial (i.e.,
                         a background noise fluctuation or a glitch)
        """
        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            template = self.templates['superevent-voevent-list-template']
            uri_kwargs = {'superevent_id': object_id}
        else:
            template = self.templates['voevent-list-template']
            uri_kwargs = {'graceid': object_id}
        uri = template.format(**uri_kwargs)

        # validate voevent_type, convert to short form if necessary
        voevent_type = self._getCode(voevent_type.lower(), self.voevent_types)
        if not voevent_type:
            raise ValueError("voevent_type must be one of: {0}".format(
                list(self.voevent_types.values())))

        # Require skymaps for 'update' and 'initial'
        if voevent_type == 'IN':
            if not skymap_filename:
                raise ValueError("Skymap file is required for 'initial' "
                    "VOEvents")

        # Construct request body
        body = {
            'voevent_type': voevent_type,
            'internal': internal,
            'open_alert': open_alert,
            'hardware_inj': hardware_inj,
            'CoincComment': CoincComment,
        }
        # Add optional args
        if skymap_type is not None:
            body['skymap_type'] = skymap_type
        if skymap_filename is not None:
            body['skymap_filename'] = skymap_filename
        if ProbHasNS is not None:
            body['ProbHasNS'] = ProbHasNS
        if ProbHasRemnant is not None:
            body['ProbHasRemnant'] = ProbHasRemnant
        if BNS is not None:
            body['BNS'] = BNS
        if NSBH is not None:
            body['NSBH'] = NSBH
        if BBH is not None:
            body['BBH'] = BBH
        if Terrestrial is not None:
            body['Terrestrial'] = Terrestrial

        return self.post(uri, body=body)

    @event_or_superevent
    def permissions(self, object_id, *args, **kwargs):
        """
        Get a list of permissions for an event or superevent.

        Signature:
            permissions(object_id)

        Arguments:
            object_id:  event graceid or superevent id

        NOTE: not currently implemented for events.
        """
        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            template = self.templates[
                'superevent-permission-list-template']
            uri_kwargs = {'superevent_id': object_id}
        else:
            raise NotImplementedError('Not implemented for events')

        uri = template.format(**uri_kwargs)
        return self.get(uri)

    @event_or_superevent
    def modify_permissions(self, object_id, action, *args, **kwargs):
        """
        Expose or hide an event or superevent to/from the public.
        Requires specific server-side permissions.

        Signature:
            modify_permissions(object_id, action)

        Arguments:
            object_id: event graceid or superevent id
            action:    'expose' or 'hide'

        NOTE: not currently implemented for events.
        """

        if (action not in ['expose', 'hide']):
            raise ValueError('action should be \'expose\' or \'hide\'')

        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            template = self.templates[
                'superevent-permission-modify-template']
            uri_kwargs = {'superevent_id': object_id}
        else:
            raise NotImplementedError('Not implemented for events')

        uri = template.format(**uri_kwargs)

        body = {'action': action}
        return self.post(uri, body=body)

    def _signoff_helper(self, object_id, action, template, uri_kwargs,
        signoff_type=None, instrument=None, status=None, comment=None):
        # uri_kwargs should already have the graceid or superevent_id in it

        # Validate args
        if signoff_type:
            signoff_type = self._getCode(signoff_type, self.signoff_types)
            if not signoff_type:
                raise ValueError("signoff_type must be one of: {0}".format(
                    ", ".join(self.signoff_types)))
        if instrument:
            instrument = self._getCode(instrument, self.instruments)
            if not instrument:
                raise ValueError("instrument must be one of: {0}".format(
                    ", ".join(self.instruments)))
        if status:
            status = self._getCode(status, self.signoff_statuses)
            if not status:
                raise ValueError("status must be one of: {0}".format(
                    ", ".join(self.signoff_statuses)))
        if signoff_type == 'OP' and not instrument:
            raise ValueError('Operator signoffs require an instrument')

        # Get HTTP method and args
        body = {}
        if (action == 'create'):
            http_method = "POST"
            body['signoff_type'] = signoff_type
            body['instrument'] = instrument
            body['comment'] = comment
            body['status'] = status
        elif (action == 'update'):
            http_method = "PATCH"
            uri_kwargs['typeinst'] = signoff_type + instrument
            if comment is not None:
                body['comment'] = comment
            if status is not None:
                body['status'] = status
        elif (action == 'get'):
            http_method = "GET"
            if signoff_type is not None:
                uri_kwargs['typeinst'] = signoff_type + instrument
        elif (action == 'delete'):
            http_method = "DELETE"
            uri_kwargs['typeinst'] = signoff_type + instrument
        else:
            raise ValueError("action should be 'create', 'update', "
                "'get', or 'delete'")
        uri = template.format(**uri_kwargs)

        # Get http method
        method = getattr(self, http_method.lower())
        if body:
            response = method(uri, body=body)
        else:
            response = method(uri)

        return response

    @event_or_superevent
    def signoffs(self, object_id, signoff_type=None, instrument='', *args,
            **kwargs):
        """
        Get a list of signoffs for an event or superevent, or a particular
        signoff.

        Signature:
            signoffs(object_id, signoff_type=None, instrument='')

        Arguments:
            object_id:    event graceid or superevent id
            signoff_type: 'OP' or 'operator' for operator signoff,
                          'ADV' or 'advocate' for advocate signoff
            instrument:   instrument abbreviation ('H1', 'L1', etc.). Blank
                          string for advocate signoffs

        NOTE: not currently implemented for events.
        """
        # Get URI template
        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            if signoff_type is not None:
                template = self.templates['superevent-signoff-detail-template']
            else:
                template = self.templates['superevent-signoff-list-template']
            uri_kwargs = {'superevent_id': object_id}
        else:
            raise NotImplementedError('Not yet implemented for events')

        return self._signoff_helper(object_id, 'get', template, uri_kwargs,
            signoff_type, instrument)

    @event_or_superevent
    def create_signoff(self, object_id, signoff_type, status, comment,
        instrument='', *args, **kwargs):

        # Get URI template
        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            template = self.templates['superevent-signoff-list-template']
            uri_kwargs = {'superevent_id': object_id}
        else:
            raise NotImplementedError('Not yet implemented for events')

        return self._signoff_helper(object_id, 'create', template, uri_kwargs,
            signoff_type=signoff_type, instrument=instrument, status=status,
            comment=comment)

    @event_or_superevent
    def update_signoff(self, object_id, signoff_type, status=None,
        comment=None, instrument='', *args, **kwargs):
        # This will make a PATCH request

        # Either status or comment must be included - otherwise the user
        # is not updating anything
        if not (status or comment):
            raise ValueError("Provide at least one of 'status' or 'comment'")

        # Get URI template
        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            template = self.templates['superevent-signoff-detail-template']
            uri_kwargs = {'superevent_id': object_id}
        else:
            raise NotImplementedError('Not yet implemented for events')

        return self._signoff_helper(object_id, 'update', template, uri_kwargs,
            signoff_type=signoff_type, instrument=instrument, status=status,
            comment=comment)

    @event_or_superevent
    def delete_signoff(self, object_id, signoff_type, instrument='', *args,
        **kwargs):
        # Get URI template
        is_superevent = kwargs.pop('is_superevent', False)
        if is_superevent:
            template = self.templates['superevent-signoff-detail-template']
            uri_kwargs = {'superevent_id': object_id}
        else:
            raise NotImplementedError('Not yet implemented for events')

        return self._signoff_helper(object_id, 'delete', template, uri_kwargs,
            signoff_type, instrument)


#-----------------------------------------------------------------
# HTTP upload encoding
# Taken from http://code.activestate.com/recipes/146306/

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = b'\r\n'
    L = []
    for (key, value) in fields:
        if value is None: continue
        L.append(('--' + BOUNDARY).encode())
        L.append('Content-Disposition: form-data; name="{0}"'
            .format(key).encode())
        L.append(''.encode())
        # encode in case it is unicode
        if isinstance(value, six.binary_type):
            L.append(value)
        elif isinstance(value, six.text_type):
            L.append(value.encode())
        else:
            L.append(str(value).encode())
    for (key, filename, value) in files:
        if value is None: continue
        L.append(('--' + BOUNDARY).encode())
        # str(filename) in case it is unicode
        L.append(('Content-Disposition: form-data; name="{0}"; '
            'filename="{1}"').format(key, filename).encode())
        L.append('Content-Type: {0}'.format(get_content_type(filename))
            .encode())
        L.append(''.encode())
        if isinstance(value, six.text_type):
            L.append(value.encode())
        else:
            L.append(value)
    L.append(('--' + BOUNDARY + '--').encode())
    L.append(''.encode())
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary={0}'.format(BOUNDARY) \
        .encode()
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

# Legacy
GraceDbBasic = GraceDb

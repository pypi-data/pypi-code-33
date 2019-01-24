# This file is part of caucase
# Copyright (C) 2017-2019  Nexedi
#     Alain Takoudjou <alain.takoudjou@nexedi.com>
#     Vincent Pelletier <vincent@nexedi.com>
#
# caucase is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caucase is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caucase.  If not, see <http://www.gnu.org/licenses/>.
"""
Caucase - Certificate Authority for Users, Certificate Authority for SErvices
"""
from __future__ import absolute_import
from Cookie import SimpleCookie, CookieError
import httplib
import json
import os
import sys
import threading
import time
from urllib import quote, urlencode
from urlparse import parse_qs
from wsgiref.util import application_uri, request_uri
import jwt
from . import utils
from . import exceptions

# pylint: disable=import-error
if sys.version_info >= (3, ): # pragma: no cover
  from html import escape
else: # pragma: no cover
  from cgi import escape
# pylint: enable=import-error

__all__ = ('Application', 'CORSTokenManager')

# TODO: l10n
CORS_FORM_TEMPLATE = b'''\
<html>
<head>
  <title>Caucase CORS access</title>
</head>
<body>
  <form action="." method="post">
    <input type="hidden" name="return_to" value="%(return_to)s"/>
    <input type="hidden" name="origin" value="%(origin)s"/>
    Your browser is trying to access caucase at <b>%(caucase)s</b>
    under the control of <b>%(origin)s</b>.<br/>
    Do you wish to grant it the permission to use your credentials ?<br/>
    <a href="%(return_to)s">Go back</a>
    <button name="grant" value="0">Deny access</button>
    <button name="grant" value="1">Grant access</button><br/>
    If you already authorised this origin and you still get redirected here,
    you may need to enable 3rd-party cookies in your browser.
  </form>
</body>
</html>
'''
CORS_FORM_ORIGIN_PARAMETER = 'origin'
CORS_FORM_RETURN_PARAMETER = 'return'
CORS_POLICY_ALWAYS_DENY = object()
CORS_POLICY_ALWAYS_ALLOW = object()
# If neither policy is set: ask user

SUBPATH_FORBIDDEN = object()
SUBPATH_REQUIRED = object()
SUBPATH_OPTIONAL = object()

CORS_COOKIE_ACCESS_KEY = 'a' # Whether user decided to grant access.
CORS_COOKIE_ORIGIN_KEY = 'o' # Prevent an origin from stealing another's token.

A_YEAR_IN_SECONDS = 60 * 60 * 24 * 365 # Roughly a year

def _getStatus(code):
  return '%i %s' % (code, httplib.responses[code])

class ApplicationError(Exception):
  """
  WSGI HTTP error base class.
  """
  status = _getStatus(httplib.INTERNAL_SERVER_ERROR)
  _response_headers = []

  @property
  def response_headers(self):
    """
    Get a copy of error's response headers.
    """
    return self._response_headers[:]

class BadRequest(ApplicationError):
  """
  HTTP bad request error
  """
  status = _getStatus(httplib.BAD_REQUEST)

class Unauthorized(ApplicationError):
  """
  HTTP unauthorized error
  """
  status = _getStatus(httplib.UNAUTHORIZED)

class SSLUnauthorized(Unauthorized):
  """
  Authentication failed because of SSL credentials (missing or incorrect)
  """
  _response_headers = [
    # Note: non standard scheme, suggested in
    # https://www.ietf.org/mail-archive/web/httpbisa/current/msg03764.html
    ('WWW-Authenticate', 'transport'),
  ]

class OriginUnauthorized(Unauthorized):
  """
  Authentication failed because "Origin" header is not authorised by user.
  AKA, CORS protection
  """
  def __init__(self, login_url, *args, **kw):
    super(OriginUnauthorized, self).__init__(*args, **kw)
    self._response_headers = [
      ('WWW-Authenticate', 'cors url=' + quote(login_url)),
    ]

class Forbidden(ApplicationError):
  """
  HTTP forbidden error
  """
  status = _getStatus(httplib.FORBIDDEN)

class NotFound(ApplicationError):
  """
  HTTP not found error
  """
  status = _getStatus(httplib.NOT_FOUND)

class BadMethod(ApplicationError):
  """
  HTTP bad method error
  """
  status = _getStatus(httplib.METHOD_NOT_ALLOWED)

  def __init__(self, allowed_list):
    super(BadMethod, self).__init__(allowed_list)
    self._response_headers = [
      ('Allow', ', '.join(allowed_list)),
    ]

class Conflict(ApplicationError):
  """
  HTTP conflict
  """
  status = _getStatus(httplib.CONFLICT)

class TooLarge(ApplicationError):
  """
  HTTP too large error
  """
  status = _getStatus(httplib.REQUEST_ENTITY_TOO_LARGE)

class InsufficientStorage(ApplicationError):
  """
  No storage slot available (not necessarily out of disk space)
  """
  # httplib lacks the textual description for 507, although it has the
  # constant...
  status = '%i Insufficient Storage' % (httplib.INSUFFICIENT_STORAGE, )

STATUS_OK = _getStatus(httplib.OK)
STATUS_CREATED = _getStatus(httplib.CREATED)
STATUS_NO_CONTENT = _getStatus(httplib.NO_CONTENT)
STATUS_FOUND = _getStatus(httplib.FOUND)
MAX_BODY_LENGTH = 10 * 1024 * 1024 # 10 MB

class CORSTokenManager(object):
  """
  CORS token producer and validator.
  Handles generating the secret needed to sign tokens, and its seamless
  renewal.
  """
  _secret_validity_period = A_YEAR_IN_SECONDS

  def __init__(self, secret_list=(), onNewKey=lambda _: None):
    """
    secret_list (list of opaque)
      Values that onNewKey received on previous instance.
    onNewKey (callable)
      Called when a new key has been generated, with the updated
      secret list as argument.
    """
    self._secret_list = sorted(secret_list, key=lambda x: x[0])
    self._onNewKey = onNewKey
    self._lock = threading.Lock()

  def sign(self, payload):
    """
    payload (any json-friendly data structure)
      The value to sign.
    Returns signed token as a string.
    """
    now = time.time()
    with self._lock:
      secret_list = self._secret_list = [
        x
        for x in self._secret_list
        if x[0] > now
      ]
      if secret_list:
        until, key = secret_list[-1]
        if until - now < self._secret_validity_period // 2:
          # Generate a new secret well ahead of previous secret's expiration.
          key = None
      else:
        key = None
      if key is None:
        key = os.urandom(32)
        secret_list.append((now + self._secret_validity_period, key))
        self._onNewKey(secret_list)
    return utils.toUnicode(jwt.encode(
      payload={'p': payload},
      key=key,
      algorithm='HS256',
    ))

  def verify(self, token, default=None):
    """
    token (str)
      Signed tokrn to validate.
    Returns token's payload if it passes checks.
    Otherwise, returns default.
    """
    for _, key in self._secret_list:
      # Note: not enforcing secret expiration at this level, as tokens should
      # expire well before any secret expires.
      try:
        return jwt.decode(
          jwt=token,
          key=key,
          algorithms=['HS256'],
        )['p']
      except jwt.InvalidTokenError:
        pass
    return default

class Application(object):
  """
  WSGI application class

  Thread- and process-safe (locks handled by sqlite3).
  """
  def __init__(
    self,
    cau,
    cas,
    http_url,
    https_url,
    cors_token_manager,
    cors_cookie_id='cors',
    cors_whitelist=(),
  ):
    """
    cau (caucase.ca.CertificateAuthority)
      CA for users.
      Will be hosted under /cau

    cas (caucase.ca.CertificateAuthority)
      CA for services.
      Will be hosted under /cas

    http_url (str)
      HTTP URL the application is hosted under.
      Used to derive HATEOAS URLs.

    https_url (str)
      HTTPS URL the application is hosted under.
      Used to derive HATEOAS URLs.

    cors_cookie_id (str)
      Cookie name to use to store CORS token.

    cors_token_manager (CORSTokenManager)
      Generates CORS token secrets.
      Application wrapper should handle some form of persistence for best user
      experience (so token survive server restarts).

    cors_whitelist (list of strings)
      List of Origin values to always trust.
    """
    self._cau = cau
    self._http_url = http_url.rstrip('/')
    self._https_url = https_url.rstrip('/')
    self._cors_cookie_id = cors_cookie_id
    self._cors_token_manager = cors_token_manager
    self._cors_whitelist = cors_whitelist
    # Routing dict structure:

    # path entry dict:
    # "method": method dict
    # "context": any object
    # "routing": routing dict

    # routing dict:
    # key: path entry (ie, everything but slashes)
    # value: path entry dict

    # method dict:
    # key: HTTP method ("GET", "POST", ...)
    # value: action dict

    # action dict:
    # "do": callable for the action
    #   If "subpath" forbidden:
    #     (context, environ) -> (status, header_list, iterator)
    #   Otherwise:
    #     (context, environ, subpath) -> (status, header_list, iterator)
    # - context is the value of the nearest path entry dict's "context", None
    #   by default.
    # - environ: wsgi environment
    # - subpath: trailing path component list
    # - status: HTTP status code & reason
    # - header_list: HTTP reponse header list (see wsgi specs)
    # - iterator: HTTP response body generator (see wsgi specs)
    # "cors": CORS policy (default: ask)
    # "descriptor": list of descriptor dicts.
    # "context_is_routing": whether context should be set to routing dict for
    #   current path, instead of nearest context dict. (default: False)
    # "subpath": whether a subpath is expected, forbidden, or optional
    #   (default: forbidden)

    # descriptor dict:
    # NON-AUTORITATIVE ! Only for HAL API auto-description generation.
    # "name": HAL action or link name (required)
    # "title": HAL title (required)
    # "subpath": HAL href trailer, must be an URL template piece (default: None)
    # "authenticated": whether the action/link requires authentication
    #   (default: False)

    caucase_routing_dict = {
      'crl': {
        'method': {
          'GET': {
            'do': self.getCertificateRevocationList,
            'descriptor': [{
              'name': 'getCertificateRevocationList',
              'title': 'Retrieve latest certificate revocation list.',
            }],
          },
        },
      },
      'csr': {
        'method': {
          'GET': {
            'do': self.getCSR,
            'subpath': SUBPATH_OPTIONAL,
            'descriptor': [{
              'name': 'getPendingCertificateRequestList',
              'title': 'List pending certificate signing requests.',
              'authenticated': True
            }, {
              'name': 'getCertificateSigningRequest',
              'title': 'Retrieve a pending certificate signing request.',
              'subpath': '{+csr_id}',
            }],
          },
          'PUT': {
            'do': self.createCertificateSigningRequest,
            'descriptor': [{
              'name': 'createCertificateSigningRequest',
              'title': 'Request a new certificate signature.',
            }],
          },
          'DELETE': {
            'do': self.deletePendingCertificateRequest,
            'subpath': SUBPATH_REQUIRED,
            'descriptor': [{
              'name': 'deletePendingCertificateRequest',
              'title': 'Reject a pending certificate signing request.',
              'subpath': '{+csr_id}',
              'authenticated': True,
            }],
          },
        },
      },
      'crt': {
        'routing': {
          'ca.crt.pem': {
            'method': {
              'GET': {
                'do': self.getCACertificate,
                'descriptor': [{
                  'name': 'getCACertificate',
                  'title': 'Retrieve current CA certificate.',
                }],
              },
            },
          },
          'ca.crt.json': {
            'method': {
              'GET': {
                'do': self.getCACertificateChain,
                'descriptor': [{
                  'name': 'getCACertificateChain',
                  'title': 'Retrieve current CA certificate trust chain.',
                }],
              },
            },
          },
          'revoke': {
            'method': {
              'PUT': {
                'do': self.revokeCertificate,
                'descriptor': [{
                  'name': 'revokeCertificate',
                  'title': 'Revoke a certificate',
                }],
              },
            },
          },
          'renew': {
            'method': {
              'PUT': {
                'do': self.renewCertificate,
                'descriptor': [{
                  'name': 'renewCertificate',
                  'title': 'Renew a certificate',
                }],
              },
            },
          },
        },
        'method': {
          'GET': {
            'do': self.getCertificate,
            'subpath': SUBPATH_REQUIRED,
            'descriptor': [{
              'name': 'getCertificate',
              'subpath': '{+csr_id}',
              'templated': True,
              'title': 'Retrieve a signed certificate.',
            }],
          },
          'PUT': {
            'do': self.createCertificate,
            'subpath': SUBPATH_REQUIRED,
            'descriptor': [{
              'name': 'createCertificate',
              'subpath': '{+crt_id}',
              'title': 'Accept pending certificate signing request',
              'templated': True,
              'authenticated': True,
             }],
          },
        },
      },
    }
    getHALMethodDict = lambda name, title: {
      'GET': {
        'do': self.getHAL,
        'context_is_routing': True,
        'cors': CORS_POLICY_ALWAYS_ALLOW,
        'descriptor': [{
          'name': name,
          'title': title,
        }],
      },
    }
    self._root_dict = {
      'method': {
        'GET': {
          # XXX: Use full-recursion getHAL instead ?
          'do': self.getTopHAL,
          'context_is_routing': True,
          'cors': CORS_POLICY_ALWAYS_ALLOW,
        },
      },
      'routing': {
        'cors': {
          'method': {
            'GET': {
              'do': self.getCORSForm,
            },
            'POST': {
              'do': self.postCORSForm,
              'cors': CORS_POLICY_ALWAYS_DENY,
            },
          },
        },
        'cas': {
          'method': getHALMethodDict('getCASHAL', 'cas'),
          'context': cas,
          'routing': caucase_routing_dict,
        },
        'cau': {
          'method': getHALMethodDict('getCAUHAL', 'cau'),
          'context': cau,
          'routing': caucase_routing_dict,
        },
      },
    }

  def __call__(self, environ, start_response):
    """
    WSGI entry point
    """
    cors_header_list = []
    try: # Convert ApplicationError subclasses into error responses
      try: # Convert exceptions into ApplicationError subclass exceptions
        path_item_list = [
          x
          for x in environ.get('PATH_INFO', '').split('/')
          if x
        ]
        path_entry_dict = self._root_dict
        context = None
        while path_item_list:
          context = path_entry_dict.get('context', context)
          try:
            path_entry_dict = path_entry_dict['routing'][path_item_list[0]]
          except KeyError:
            break
          del path_item_list[0]
        try:
          method_dict = path_entry_dict['method']
        except KeyError:
          raise NotFound
        request_method = environ['REQUEST_METHOD']
        try:
          action_dict = method_dict[request_method]
        except KeyError:
          if request_method == 'OPTIONS':
            status = STATUS_NO_CONTENT
            header_list = []
            result = []
            self._checkCORSAccess(
              environ=environ,
              # Pre-flight is always allowed.
              policy=CORS_POLICY_ALWAYS_ALLOW,
              header_list=cors_header_list,
              preflight=True,
            )
            if cors_header_list:
              # CORS headers added, add more
              self._optionAddCORSHeaders(method_dict, cors_header_list)
          else:
            raise BadMethod(method_dict.keys() + ['OPTIONS'])
        else:
          subpath = action_dict.get('subpath', SUBPATH_FORBIDDEN)
          if (
            subpath is SUBPATH_FORBIDDEN and path_item_list or
            subpath is SUBPATH_REQUIRED and not path_item_list
          ):
            raise NotFound
          self._checkCORSAccess(
            environ=environ,
            policy=action_dict.get('cors'),
            header_list=cors_header_list,
            preflight=False,
          )
          if action_dict.get('context_is_routing'):
            context = path_entry_dict.get('routing')
          kw = {
            'context': context,
            'environ': environ,
          }
          if subpath != SUBPATH_FORBIDDEN:
            kw['subpath'] = path_item_list
          status, header_list, result = action_dict['do'](**kw)
      except ApplicationError:
        raise
      except exceptions.NotFound:
        raise NotFound
      except exceptions.Found:
        raise Conflict
      except exceptions.NoStorage:
        raise InsufficientStorage
      except exceptions.NotJSON:
        raise BadRequest(b'Invalid json payload')
      except exceptions.CertificateAuthorityException as e:
        raise BadRequest(str(e))
      except Exception:
        utils.log_exception(
          error_file=environ['wsgi.errors'],
          exc_info=sys.exc_info(),
          client_address=environ.get('REMOTE_ADDR', ''),
        )
        raise ApplicationError
    except ApplicationError as e:
      status = e.status
      header_list = e.response_headers
      result = [utils.toBytes(str(x)) for x in e.args]
    # Note: header_list and cors_header_list are expected to contain
    # distinct header sets. This may not always stay true for "Vary".
    header_list.extend(cors_header_list)
    header_list.append(('Date', utils.timestamp2IMFfixdate(time.time())))
    start_response(status, header_list)
    return result

  @staticmethod
  def _returnFile(data, content_type, header_list=None):
    if header_list is None:
      header_list = []
    header_list.append(('Content-Type', content_type))
    header_list.append(('Content-Length', str(len(data))))
    return (STATUS_OK, header_list, [data])

  @staticmethod
  def _getCSRID(subpath):
    try:
      crt_id, = subpath
    except ValueError:
      raise NotFound
    try:
      return int(crt_id)
    except ValueError:
      raise BadRequest(b'Invalid integer')

  @staticmethod
  def _read(environ):
    """
    Read the entire request body.

    Raises BadRequest if request Content-Length cannot be parsed.
    Raises TooLarge if Content-Length if over MAX_BODY_LENGTH.
    If Content-Length is not set, reads at most MAX_BODY_LENGTH bytes.
    """
    try:
      length = int(environ.get('CONTENT_LENGTH') or MAX_BODY_LENGTH)
    except ValueError:
      raise BadRequest(b'Invalid Content-Length')
    if length > MAX_BODY_LENGTH:
      raise TooLarge(b'Content-Length limit exceeded')
    return environ['wsgi.input'].read(length)

  def _authenticate(self, environ, header_list):
    """
    Verify user authentication.

    Raises SSLUnauthorized if authentication does not pass checks.
    On success, appends a "Cache-Control" header.
    """
    try:
      ca_list = self._cau.getCACertificateList()
      utils.load_certificate(
        environ.get('SSL_CLIENT_CERT', b''),
        trusted_cert_list=ca_list,
        crl=utils.load_crl(
          self._cau.getCertificateRevocationList(),
          ca_list,
        ),
      )
    except (exceptions.CertificateVerificationError, ValueError):
      raise SSLUnauthorized
    header_list.append(('Cache-Control', 'private'))

  def _readJSON(self, environ):
    """
    Read request body and convert to json object.

    Raises BadRequest if request Content-Type is not 'application/json', or if
    json decoding fails.
    """
    if environ.get('CONTENT_TYPE') != 'application/json':
      raise BadRequest(b'Bad Content-Type')
    data = self._read(environ)
    try:
      return json.loads(data)
    except ValueError:
      raise BadRequest(b'Invalid json')

  def _createCORSCookie(self, environ, value):
    """
    Create a new CORS cookie with given content.

    environ (dict)
      To decide cookie's scope (path).
    value (string)
      Cookie's raw value.

    Returns a Morsel instance.
    """
    cookie = SimpleCookie({self._cors_cookie_id: value})[self._cors_cookie_id]
    cookie['path'] = environ.get('SCRIPT_NAME') or '/',
    cookie['expires'] = A_YEAR_IN_SECONDS
    # No "secure" flag: cookie is not secret, and is protected against
    # tampering on client side.
    # No "httponly" flag: cookie is protected against tampering on client side,
    # and this allows a GUI to list allowed origins and let user delete some
    # (which may not prevent a hostile client from restoring its access for
    # the validity period of their entry - a year by default).
    return cookie

  @staticmethod
  def _optionAddCORSHeaders(method_dict, header_list):
    header_list.append((
      'Access-Control-Allow-Methods',
      ', '.join(
        [
          x
          for x, y in method_dict.iteritems()
          if y.get('cors') is not CORS_POLICY_ALWAYS_DENY
        ] + ['OPTIONS'],
      ),
    ))
    header_list.append((
      'Access-Control-Allow-Headers',
      # Only list values which are not:
      # - safelisted names for their safe values
      # - forbidden names (handled by user agent, not controlled by script)
      'Content-Type, User-Agent',
    ))

  def _checkCORSAccess(
    self,
    environ,
    policy,
    header_list,
    preflight,
  ):
    """
    Check whether access should be allowed, based on origin:
    - allow (return)
    - deny (raise Forbidden)
    - request user approval (raise OriginUnauthorized)
    When allowing, populate header_list with CORS header when in a cross-origin
    context.
    "null" origin (aka "sensitive origin") always gets Forbidden instead of
    OriginUnauthorized.
    header_list may be modified before raising OriginUnauthorized, in order to
    give client an opportunity to clean stale/broken values.
    """
    my_origin = application_uri(environ).split('/', 1)[0]
    origin = environ.get('HTTP_ORIGIN', my_origin)
    if origin == my_origin:
      # Not a CORS request
      return
    if (
      policy is CORS_POLICY_ALWAYS_ALLOW or
      origin in self._cors_whitelist
    ):
      access = True
    elif policy is CORS_POLICY_ALWAYS_DENY or origin == 'null':
      access = False
    else:
      cookie = SimpleCookie(environ.get('HTTP_COOKIE', ''))
      try:
        origin_control_dict = json.loads(cookie[self._cors_cookie_id].value)
        access_dict = origin_control_dict[origin]
      except KeyError:
        # Missing cookie or origin
        access = None
      except ValueError:
        # Malformed cookie, tell client to discard it
        cookie = self._createCORSCookie(environ, '')
        cookie['expires'] = 'Thu, 1 Jan 1970 00:00:00 GMT'
        header_list.append(
          ('Set-Cookie', cookie.OutputString()),
        )
        access = None
      else:
        access_dict = self._cors_token_manager.verify(access_dict, {})
        if access_dict.get(CORS_COOKIE_ORIGIN_KEY) == origin:
          access = access_dict.get(CORS_COOKIE_ACCESS_KEY)
        else:
          # Invalid or expired entry for origin, tell client to store
          # a new cookie without it.
          access = None
          del origin_control_dict[origin]
          header_list.append(
            (
              'Set-Cookie',
              self._createCORSCookie(
                environ,
                json.dumps(origin_control_dict),
              ).OutputString(),
            ),
          )
      if access is None:
        # Missing or malformed cookie, missing or expired or invalid entry
        # for origin: require authentication via cors form.
        raise OriginUnauthorized(
          self._https_url + '/cors?' +
          urlencode([(CORS_FORM_ORIGIN_PARAMETER, origin)]) +
          '{&' + CORS_FORM_RETURN_PARAMETER + '}',
        )
    if access:
      header_list.append(('Access-Control-Allow-Credentials', 'true'))
      header_list.append(('Access-Control-Allow-Origin', origin))
      if not preflight:
        header_list.append((
          'Access-Control-Expose-Headers',
          # Only list values which are not:
          # - safelisted names for their safe values
          # - forbidden names (handled by user agent, not controlled by script)
          'Location, WWW-Authenticate',
        ))
      header_list.append(('Vary', 'Origin'))
    else:
      raise Forbidden

  def getTopHAL(self, context, environ):
    """
    Handle GET / .
    """
    return self.getHAL(context, environ, recurse=False)

  def getHAL(self, context, environ, recurse=True):
    """
    Handle GET /{,context} .
    """
    https_url = self._https_url
    http_url = (
      # Do not advertise http URLs when accessed in https: client already
      # decided to trust our certificate, do not lead them away.
      https_url
      if environ['wsgi.url_scheme'] == 'https' else
      self._http_url
    )
    hal = {
      '_links': {
        'self': {
          'href': request_uri(environ, include_query=False).rstrip('/'),
        },
      },
    }
    path_info = environ.get('PATH_INFO', '').rstrip('/')
    if path_info:
      hal['_links']['home'] = {
        'href': application_uri(environ),
      }
    routing_dict_list = [(
      (environ.get('SCRIPT_NAME', '') + path_info) or '/',
      context,
    )]
    while routing_dict_list:
      routing_path, routing_dict = routing_dict_list.pop()
      for component, path_entry_dict in routing_dict.iteritems():
        component_path = routing_path + '/' + component
        if recurse and 'routing' in path_entry_dict:
          routing_dict_list.append((
            component_path,
            path_entry_dict['routing'],
          ))
        for method, action_dict in path_entry_dict['method'].iteritems():
          for action in action_dict.get('descriptor', ()):
            descriptor_dict = {
              'title': action['title'],
            }
            action_url = (
                https_url
                if action.get('authenticated') else
                http_url
            ) + component_path
            if 'subpath' in action:
              action_url += '/' + action['subpath']
              descriptor_dict['templated'] = True
            descriptor_dict['href'] = action_url
            if method == 'GET':
              hal_section_id = '_links'
            else:
              descriptor_dict['method'] = method
              hal_section_id = '_actions'
            hal_section_dict = hal.setdefault(hal_section_id, {})
            name = action['name']
            assert name not in hal_section_dict, name
            hal_section_dict[name] = descriptor_dict
    return self._returnFile(
      utils.toBytes(json.dumps(hal)),
      'application/hal+json',
    )

  def getCORSForm(self, context, environ): # pylint: disable=unused-argument
    """
    Handle GET /cors .
    """
    if environ['wsgi.url_scheme'] != 'https':
      return (
        STATUS_FOUND,
        [
          ('Location', self._https_url),
        ],
        [],
      )
    try:
      query = parse_qs(environ['QUERY_STRING'], strict_parsing=True)
      origin, = query[CORS_FORM_ORIGIN_PARAMETER]
      return_to, = query[CORS_FORM_RETURN_PARAMETER]
    except (KeyError, ValueError):
      raise BadRequest
    return self._returnFile(
      CORS_FORM_TEMPLATE % {
        b'caucase': utils.toBytes(escape(self._http_url, quote=True)),
        b'return_to': utils.toBytes(escape(return_to, quote=True)),
        b'origin': utils.toBytes(escape(origin, quote=True)),
      },
      'text/html',
      [
        # Anti-clickjacking headers
        # Standard, apparently not widespread yet
        ('Content-Security-Policy', "frame-ancestors 'none'"),
        # BBB
        ('X-Frame-Options', 'DENY'),
      ],
    )

  def postCORSForm(self, context, environ): # pylint: disable=unused-argument
    """
    Handle POST /cors .
    """
    if environ['wsgi.url_scheme'] != 'https':
      raise NotFound
    if environ.get('CONTENT_TYPE') != 'application/x-www-form-urlencoded':
      raise BadRequest(b'Unhandled Content-Type')
    try:
      form_dict = parse_qs(self._read(environ), strict_parsing=True)
      origin, = form_dict['origin']
      return_to, = form_dict['return_to']
      grant, = form_dict['grant']
      grant = bool(int(grant))
    except (KeyError, ValueError, TypeError):
      raise BadRequest
    try:
      origin_control_dict = json.loads(
        SimpleCookie(environ['HTTP_COOKIE'])[self._cors_cookie_id].value,
      )
    except (CookieError, KeyError, ValueError):
      origin_control_dict = {}
    origin_control_dict[origin] = self._cors_token_manager.sign({
      CORS_COOKIE_ACCESS_KEY: grant,
      CORS_COOKIE_ORIGIN_KEY: origin,
    })
    return (
      STATUS_FOUND,
      [
        ('Location', return_to),
        (
          'Set-Cookie',
          self._createCORSCookie(
            environ,
            json.dumps(origin_control_dict),
          ).OutputString(),
        ),
      ],
      [],
    )

  def getCertificateRevocationList(
    self,
    context,
    environ,
  ): # pylint: disable=unused-argument
    """
    Handle GET /{context}/crl .
    """
    return self._returnFile(
      context.getCertificateRevocationList(),
      'application/pkix-crl',
    )

  def getCSR(self, context, environ, subpath):
    """
    Handle GET /{context}/csr/{csr_id} and GET /{context}/csr.
    """
    if subpath:
      return self._returnFile(
        context.getCertificateSigningRequest(self._getCSRID(subpath)),
        'application/pkcs10',
      )
    header_list = []
    self._authenticate(environ, header_list)
    return self._returnFile(
      utils.toBytes(json.dumps(context.getCertificateRequestList())),
      'application/json',
      header_list,
    )

  def createCertificateSigningRequest(self, context, environ):
    """
    Handle PUT /{context}/csr .
    """
    try:
      csr_id = context.appendCertificateSigningRequest(self._read(environ))
    except exceptions.NotACertificateSigningRequest:
      raise BadRequest(b'Not a valid certificate signing request')
    return (STATUS_CREATED, [('Location', str(csr_id))], [])

  def deletePendingCertificateRequest(self, context, environ, subpath):
    """
    Handle DELETE /{context}/csr/{csr_id} .
    """
    # Note: single-use variable to verify subpath before allocating more
    # resources to this request
    csr_id = self._getCSRID(subpath)
    header_list = []
    self._authenticate(environ, header_list)
    try:
      context.deletePendingCertificateSigningRequest(csr_id)
    except exceptions.NotFound:
      raise NotFound
    return (STATUS_NO_CONTENT, header_list, [])

  def getCACertificate(
    self,
    context,
    environ,
  ): # pylint: disable=unused-argument
    """
    Handle GET /{context}/crt/ca.crt.pem urls.
    """
    return self._returnFile(
      context.getCACertificate(),
      'application/x-x509-ca-cert',
    )

  def getCACertificateChain(
    self,
    context,
    environ,
  ): # pylint: disable=unused-argument
    """
    Handle GET /{context}/crt/ca.crt.json urls.
    """
    return self._returnFile(
      utils.toBytes(json.dumps(context.getValidCACertificateChain())),
      'application/json',
    )

  def getCertificate(
    self,
    context,
    environ,
    subpath,
  ): # pylint: disable=unused-argument
    """
    Handle GET /{context}/crt/{crt_id} urls.
    """
    return self._returnFile(
      context.getCertificate(self._getCSRID(subpath)),
      'application/pkix-cert',
    )

  def revokeCertificate(self, context, environ):
    """
    Handle PUT /{context}/crt/revoke .
    """
    header_list = []
    data = self._readJSON(environ)
    if data['digest'] is None:
      self._authenticate(environ, header_list)
      payload = utils.nullUnwrap(data)
      if 'revoke_crt_pem' not in payload:
        context.revokeSerial(payload['revoke_serial'])
        return (STATUS_NO_CONTENT, header_list, [])
    else:
      payload = utils.unwrap(
        data,
        lambda x: x['revoke_crt_pem'],
        context.digest_list,
      )
    context.revoke(
      crt_pem=utils.toBytes(payload['revoke_crt_pem']),
    )
    return (STATUS_NO_CONTENT, header_list, [])

  def renewCertificate(self, context, environ):
    """
    Handle PUT /{context}/crt/renew .
    """
    payload = utils.unwrap(
      self._readJSON(environ),
      lambda x: x['crt_pem'],
      context.digest_list,
    )
    return self._returnFile(
      context.renew(
        crt_pem=utils.toBytes(payload['crt_pem']),
        csr_pem=utils.toBytes(payload['renew_csr_pem']),
      ),
      'application/pkix-cert',
    )

  def createCertificate(self, context, environ, subpath):
    """
    Handle PUT /{context}/crt/{crt_id} urls.
    """
    # Note: single-use variable to verify subpath before allocating more
    # resources to this request
    crt_id = self._getCSRID(subpath)
    body = self._read(environ)
    if not body:
      template_csr = None
    elif environ.get('CONTENT_TYPE') == 'application/pkcs10':
      template_csr = utils.load_certificate_request(body)
    else:
      raise BadRequest(b'Bad Content-Type')
    header_list = []
    self._authenticate(environ, header_list)
    context.createCertificate(
      csr_id=crt_id,
      template_csr=template_csr,
    )
    return (STATUS_NO_CONTENT, header_list, [])

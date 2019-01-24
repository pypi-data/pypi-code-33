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

Test suite
"""
# pylint: disable=too-many-lines, too-many-public-methods
from __future__ import absolute_import
import contextlib
from Cookie import SimpleCookie
import datetime
import errno
import functools
import glob
import HTMLParser
import httplib
from io import BytesIO, StringIO
import ipaddress
import json
import os
import random
import shutil
import socket
import sqlite3
import ssl
import sys
import tempfile
import threading
import time
import unittest
from urllib import quote, urlencode
import urlparse
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from caucase import cli
from caucase.ca import Extension
from caucase.client import CaucaseError, CaucaseClient
from caucase.exceptions import CertificateVerificationError
# Do not import caucase.http into this namespace: 2to3 will import standard
# http module, which will then be masqued by caucase's http submodule.
import caucase.http
from caucase import utils
from caucase import exceptions
from caucase import wsgi
from caucase.storage import SQLite3Storage

_cryptography_backend = default_backend()

NOT_CAUCASE_OID = '2.25.285541874270823339875695650038637483518'
A_YEAR_IN_SECONDS = 60 * 60 * 24 * 365 # Roughly a year

class assertHTMLNoScriptAlert(HTMLParser.HTMLParser):
  """
  Raise AssertionError if it finds a <script> tag containing "alert".
  """
  _in_script = False

  def __init__(self, data):
    HTMLParser.HTMLParser.__init__(self)
    self.feed(data)
    self.close()

  def reset(self):
    """
    Out of script tag.
    """
    HTMLParser.HTMLParser.reset(self)
    self._in_script = False

  def handle_starttag(self, tag, attrs):
    """
    Update whether a script tag was entered.
    """
    assert not self._in_script
    self._in_script = tag == 'script'

  def handle_endtag(self, tag): # pragma: no cover
    """
    Track leaving script tag.
    """
    if tag == 'script':
      assert self._in_script
      self._in_script = False

  def handle_data(self, data):
    """
    Check script tag content.
    """
    assert not self._in_script or 'alert' not in data, (
      '<script>...alert...</script> found'
    )

def canConnect(address): # pragma: no cover
  """
  Returns True if a connection can be established to given address, False
  otherwise.
  """
  try:
    sock = socket.create_connection(address)
  except socket.error as e:
    if e.errno == errno.ECONNREFUSED:
      return False
    raise
  else:
    sock.close()
  return True

def retry(callback, try_count=200, try_delay=0.1): # pragma: no cover
  """
  Poll <callback> every <try_delay> for <try_count> times or until it returns
  a true value.
  Always returns the value returned by latest callback invocation.
  """
  for _ in xrange(try_count):
    result = callback()
    if result:
      break
    time.sleep(try_delay)
  return result

class FakeStreamRequest(object):
  """
  For testing StreamRequestHandler subclasses
  (like caucase.http.CaucaseWSGIRequestHandler).
  """
  def __init__(self, rfile, wfile):
    """
    rfile & wfile: Both halves of emulated socket.
    """
    self._rfile = rfile
    self._wfile = wfile

  def makefile(self, mode, _):
    """
    Fake splitting the socket.
    """
    return self._rfile if 'r' in mode else self._wfile

  # pylint: disable=unused-argument
  def sendall(self, data, flags=None): # pragma: no cover
    """
    Redirect sendall.
    """
    self._wfile.write(data)
  # pylint: enable=unused-argument

class NoCloseFileProxy(object):
  """
  Intercept .close() calls, for example to allow reading StringIO content
  despite attempted closure.
  """
  def __init__(self, real_file):
    """
    real_file: Object toforward all non-close calls to.
    """
    self._real_file = real_file

  def __getattr__(self, name):
    return getattr(self._real_file, name)

  def close(self): # pragma: no cover
    """
    Don't.
    """
    pass

class FakeAppServer(object):
  """
  Minimal fake WSGI app server.
  """
  def __init__(self, app):
    self._app = app
    self.base_environ = {}

  def get_app(self):
    """
    Retrieve app.
    """
    return self._app

class DummyApp(object):
  """
  Simple WSGI app with limited (but simple) scripting.
  """
  def __init__(self, callback=lambda x: []):
    """
    callback (callable)
      Received environ as argument,
      Expected to return response body as an iterable.
    """
    self._callback = callback

  def __call__(self, environ, start_response):
    """
    WSGI entry point
    """
    start_response('200 OK', [])
    return self._callback(environ)

ON_EVENT_RAISE = object()
ON_EVENT_EXPIRE = object()
class UntilEvent(object):
  """
  Like utils.until, but with a threading.Event replacing
  KeyboardInterrupt as the early interruption source.
  """
  def __init__(self, event):
    """
    event (Event)
      Event to wait upon. Set and cleared outside this class.
    """
    self._event = event
    self._action = ON_EVENT_RAISE
    self._wait_event = threading.Event()
    self._wait_event.clear()

  @property
  def action(self):
    """
    Retrieve current action. Not very useful.
    """
    return self._action # pragma: no cover

  @action.setter
  def action(self, value):
    """
    Change the action which will happen on next event wakeup.
    """
    if value not in (ON_EVENT_RAISE, ON_EVENT_EXPIRE):
      raise ValueError # pragma: no cover
    self._action = value

  def wait(self, timeout=10):
    """
    Wait for event to be waited upon at least once.
    timeout (float)
      Maximum number of seconds to wait for.
    """
    if not self._wait_event.wait(timeout): # pragma: no cover
      raise AssertionError('Timeout reached')
    self._wait_event.clear()

  def __call__(self, deadline):
    """
    Sleep until event is set, then
    - if self.action is ON_EVENT_RAISE, raises utils.SleepInterrupt.
    - if self.action is ON_EVENT_EXPIRE, deadline time it returned.
    """
    now = datetime.datetime.utcnow()
    if now < deadline:
      self._wait_event.set()
      assert self._event.wait(10)
      self._event.clear()
      if self._action is ON_EVENT_EXPIRE:
        now = deadline
      else:
        raise utils.SleepInterrupt
    return now

def print_buffer_on_error(func):
  """
  Write output buffer to stdout when wrapped method raises.
  func is expected to be a method from CaucaseTest class.
  """
  @functools.wraps(func)
  def wrapper(self, *args, **kw):
    """
    Write output buffer to stdout when wrapped method raises.
    """
    try:
      return func(self, *args, **kw)
    except Exception: # pragma : no cover
      sys.stdout.write(utils.toBytes(os.linesep))
      sys.stdout.write(self.caucase_test_output.getvalue())
      raise
  return wrapper

@contextlib.contextmanager
def captureStdout():
  """
  Replace stdout with a BytesIO object for the duration of the context manager,
  and provide it to caller.
  """
  orig_stdout = sys.stdout
  sys.stdout = stdout = BytesIO()
  try:
    yield stdout
  finally:
    sys.stdout = orig_stdout

class CaucaseTest(unittest.TestCase):
  """
  Test a complete caucase setup: spawn a caucase-http server on CAUCASE_NETLOC
  and use caucase-cli to access it.
  """
  _server = None

  def setUp(self):
    """
    Prepare test data directory and file paths, and start caucased as most
    tests will need to interact with it.
    """
    self._data_dir = data_dir = tempfile.mkdtemp(prefix='caucase_test_')

    self._client_dir = client_dir = os.path.join(data_dir, 'client')
    os.mkdir(client_dir)
    # pylint: disable=bad-whitespace
    self._client_ca_crt      = os.path.join(client_dir, 'cas.crt.pem')
    self._client_user_ca_crt = os.path.join(client_dir, 'cau.crt.pem')
    self._client_crl         = os.path.join(client_dir, 'cas.crl.pem')
    self._client_user_crl    = os.path.join(client_dir, 'cau.crl.pem')
    # pylint: enable=bad-whitespace

    self._server_event = threading.Event()
    self._server_dir = server_dir = os.path.join(data_dir, 'server')
    os.mkdir(server_dir)
    # pylint: disable=bad-whitespace
    self._server_db          = os.path.join(server_dir, 'caucase.sqlite')
    self._server_key         = os.path.join(server_dir, 'server.key.pem')
    self._server_backup_path = os.path.join(server_dir, 'backup')
    self._server_cors_store  = os.path.join(server_dir, 'cors.key')
    # pylint: enable=bad-whitespace
    self.caucase_test_output = BytesIO()
    os.mkdir(self._server_backup_path)

    self._server_netloc = netloc = os.getenv(
      'CAUCASE_NETLOC',
      'localhost:8000',
    )
    self._caucase_url = 'http://' + netloc
    parsed_url = urlparse.urlparse(self._caucase_url)
    self.assertFalse(
      canConnect((parsed_url.hostname, parsed_url.port)),
      'Something else is already listening on %r, define CAUCASE_NETLOC '
      'environment variable with a different ip/port' % (netloc, ),
    )
    self._startServer()

  @print_buffer_on_error
  def tearDown(self):
    """
    Stop any running caucased and delete all test data files.
    """
    if self._server.is_alive():
      self._stopServer()
    shutil.rmtree(self._data_dir)

  @staticmethod
  def _getCAKeyPair(extension_list=(), not_before=None, not_after=None):
    """
    Build a reasonably-realistic CA, return key & self-signed cert.
    """
    if not_before is None:
      not_before = datetime.datetime.utcnow()
    if not_after is None:
      not_after = not_before + datetime.timedelta(10, 0)
    private_key = utils.generatePrivateKey(2048)
    subject = x509.Name([
      x509.NameAttribute(
        oid=x509.oid.NameOID.COMMON_NAME,
        value=u'John Doe CA',
      ),
    ])
    public_key = private_key.public_key()
    subject_key_identifier = x509.SubjectKeyIdentifier.from_public_key(
      public_key,
    )
    return private_key, x509.CertificateBuilder(
      subject_name=subject,
      issuer_name=subject,
      not_valid_before=not_before,
      not_valid_after=not_after,
      serial_number=x509.random_serial_number(),
      public_key=public_key,
      extensions=[
        Extension(
          subject_key_identifier,
          critical=False, # "MUST mark this extension as non-critical"
        ),
        Extension(
          x509.AuthorityKeyIdentifier.from_issuer_subject_key_identifier(
            # Dummy extension, from_issuer_subject_key_identifier accesses
            # .data directly
            Extension(
              subject_key_identifier,
              critical=False,
            ),
          ),
          critical=False, # "MUST mark this extension as non-critical"
        ),
        Extension(
          x509.BasicConstraints(
            ca=True,
            path_length=0,
          ),
          critical=True, # "MUST mark the extension as critical"
        ),
        Extension(
          x509.KeyUsage(
            # pylint: disable=bad-whitespace
            digital_signature =False,
            content_commitment=False,
            key_encipherment  =False,
            data_encipherment =False,
            key_agreement     =False,
            key_cert_sign     =True,
            crl_sign          =True,
            encipher_only     =False,
            decipher_only     =False,
            # pylint: enable=bad-whitespace
          ),
          critical=True, # "SHOULD mark this extension critical"
        ),
      ] + list(extension_list),
    ).sign(
      private_key=private_key,
      algorithm=hashes.SHA256(),
      backend=_cryptography_backend,
    )

  @staticmethod
  def _getKeyPair(
    ca_key,
    ca_crt,
    extension_list=(),
    not_before=None,
    not_after=None,
  ):
    """
    Build a reasonably-realistic signed cert, return key & self-signed cert.
    """
    if not_before is None:
      not_before = datetime.datetime.utcnow()
    if not_after is None:
      not_after = not_before + datetime.timedelta(10, 0)
    crt_key = utils.generatePrivateKey(2048)
    return crt_key, x509.CertificateBuilder(
      subject_name=x509.Name([
        x509.NameAttribute(
          oid=x509.oid.NameOID.ORGANIZATIONAL_UNIT_NAME,
          value=u'Jane Doe',
        ),
      ]),
      issuer_name=ca_crt.subject,
      not_valid_before=not_before,
      not_valid_after=not_after,
      serial_number=x509.random_serial_number(),
      public_key=crt_key.public_key(),
      extensions=[
        Extension(
          x509.KeyUsage(
            # pylint: disable=bad-whitespace
            digital_signature =True,
            content_commitment=False,
            key_encipherment  =True,
            data_encipherment =False,
            key_agreement     =False,
            key_cert_sign     =False,
            crl_sign          =False,
            encipher_only     =False,
            decipher_only     =False,
            # pylint: enable=bad-whitespace
          ),
          critical=True,
        ),
      ] + list(extension_list),
    ).sign(
      private_key=ca_key,
      algorithm=hashes.SHA256(),
      backend=_cryptography_backend,
    )

  def _skipIfOpenSSLDoesNotSupportIPContraints(self):
    ca_key, ca_crt = self._getCAKeyPair(
      extension_list=[
        Extension(
          x509.NameConstraints(
            permitted_subtrees=[
              x509.IPAddress(ipaddress.ip_network(u'127.0.0.1')),
            ],
            excluded_subtrees=None,
          ),
          critical=True,
        ),
      ],
    )
    _, crt = self._getKeyPair(
      ca_key=ca_key,
      ca_crt=ca_crt,
    )
    try:
      # pylint: disable=protected-access
      utils._verifyCertificateChain(
        cert=crt,
        trusted_cert_list=[ca_crt],
        crl=None,
      )
      # pylint: enable=protected-access
    except CertificateVerificationError: # pragma: no cover
      raise unittest.SkipTest('OpenSSL versoin does not support IP constraints')

  def _restoreServer(
    self,
    backup_path,
    key_path,
    new_csr_path,
    new_key_path,
  ):
    """
    Start caucased-manage --restore-backup .
    Returns its exit status.
    """
    try:
      caucase.http.manage(
        argv=(
          '--db', self._server_db,
          '--restore-backup',
          backup_path,
          key_path,
          new_csr_path,
          new_key_path,
        ),
      )
    except SystemExit as e:
      return e.code # pragma: no cover
    except: # pylint: disable=bare-except
      return 1
    return 0

  def _startServer(self, *argv):
    """
    Start caucased server
    """
    self._server_until = until = UntilEvent(self._server_event)
    self._server = server = threading.Thread(
      target=caucase.http.main,
      kwargs={
        'argv': (
          '--db', self._server_db,
          '--server-key', self._server_key,
          '--netloc', self._server_netloc,
          #'--threshold', '31',
          #'--key-len', '2048',
          '--cors-key-store', self._server_cors_store,
        ) + argv,
        'until': until,
        'log_file': self.caucase_test_output,
        'error_file': self.caucase_test_output,
      }
    )
    server.daemon = True
    server.start()
    parsed_url = urlparse.urlparse(self._caucase_url)
    if not retry(
      lambda: (
        self.assertTrue(server.is_alive(), 'caucased crashed on startup') or
        canConnect((parsed_url.hostname, parsed_url.port))
      ),
    ): # pragma: no cover
      self._stopServer()
      raise AssertionError('Could not connect to %r after 1 second' % (
        self._caucase_url,
      ))

  def _stopServer(self):
    """
    Stop a running caucased server
    """
    server = self._server
    self._server_until.action = ON_EVENT_RAISE
    self._server_event.set()
    server.join(2)
    if server.is_alive(): # pragma: no cover
      raise ValueError('%r does not wish to die' % (server, ))

  def _runClient(self, *argv):
    """
    Run client with given arguments.

    Returns stdout.
    """
    with captureStdout() as stdout:
      try:
        cli.main(
          argv=(
            '--ca-url', self._caucase_url,
            '--ca-crt', self._client_ca_crt,
            '--user-ca-crt', self._client_user_ca_crt,
            '--crl', self._client_crl,
            '--user-crl', self._client_user_crl,
          ) + argv,
        )
      except SystemExit:
        pass
    return stdout.getvalue()

  @staticmethod
  def _setCertificateRemainingLifeTime(key, crt, delta):
    """
    Re-sign <crt> with <key>, shifting both its not_valid_before and
    not_valid_after dates so that its remaining validity period
    becomes <delta> and its validity span stays unchanged.
    """
    new_not_valid_after_date = datetime.datetime.utcnow() + delta
    return x509.CertificateBuilder(
      subject_name=crt.subject,
      issuer_name=crt.issuer,
      not_valid_before=new_not_valid_after_date - (
        crt.not_valid_after - crt.not_valid_before
      ),
      not_valid_after=new_not_valid_after_date,
      serial_number=crt.serial_number,
      public_key=crt.public_key(),
      extensions=crt.extensions,
    ).sign(
      private_key=key,
      algorithm=crt.signature_hash_algorithm,
      backend=_cryptography_backend,
    )

  def _setCACertificateRemainingLifeTime(self, mode, serial, delta):
    """
    Find the CA certificate with <serial> in caucase <mode> ("service"
    or "user") and pass it to _setCertificateRemainingLifeTime with <delta>.
    """
    int(serial) # Must already be an integer
    prefix = {
      'user': 'cau',
      'service': 'cas',
    }[mode]
    db = sqlite3.connect(self._server_db)
    db.row_factory = sqlite3.Row
    with db:
      c = db.cursor()
      c.execute(
        'SELECT rowid, key, crt FROM ' + prefix + 'ca',
      )
      while True:
        row = c.fetchone()
        if row is None: # pragma: no cover
          raise Exception('CA with serial %r not found' % (serial, ))
        crt = utils.load_ca_certificate(utils.toBytes(row['crt']))
        if crt.serial_number == serial:
          new_crt = self._setCertificateRemainingLifeTime(
            key=utils.load_privatekey(utils.toBytes(row['key'])),
            crt=crt,
            delta=delta,
          )
          new_crt_pem = utils.dump_certificate(new_crt)
          c.execute(
            'UPDATE ' + prefix + 'ca SET '
            'expiration_date=?, crt=? '
            'WHERE rowid=?',
            (
              utils.datetime2timestamp(new_crt.not_valid_after),
              new_crt_pem,
              row['rowid'],
            ),
          )
          return new_crt_pem

  def _getBaseName(self):
    """
    Returns a random file name, prefixed by data directory.
    """
    return os.path.join(
      self._data_dir,
      str(random.getrandbits(32)),
    )

  @staticmethod
  def _createPrivateKey(basename, key_len=2048):
    """
    Create a private key and store it to file.
    """
    name = basename + '.key.pem'
    assert not os.path.exists(name)
    with open(name, 'wb') as key_file:
      key_file.write(utils.dump_privatekey(
        utils.generatePrivateKey(key_len=key_len),
      ))
    return name

  @staticmethod
  def _getBasicCSRBuilder():
    """
    Initiate a minimal CSR builder.
    """
    return x509.CertificateSigningRequestBuilder(
      subject_name=x509.Name([
        x509.NameAttribute(
          oid=x509.oid.NameOID.COMMON_NAME,
          value=u'test',
        ),
      ]),
    )

  @staticmethod
  def _finalizeCSR(basename, key_path, csr_builder):
    """
    Sign, serialise and store given CSR Builder to file.
    """
    name = basename + '.csr.pem'
    assert not os.path.exists(name)
    with open(name, 'wb') as csr_file:
      csr_file.write(
        utils.dump_certificate_request(
          csr_builder.sign(
            private_key=utils.load_privatekey(utils.getKey(key_path)),
            algorithm=utils.DEFAULT_DIGEST_CLASS(),
            backend=_cryptography_backend,
          ),
        ),
      )
    return name

  def _createBasicCSR(self, basename, key_path):
    """
    Creates a basic CSR and returns its path.
    """
    return self._finalizeCSR(
      basename,
      key_path,
      self._getBasicCSRBuilder(),
    )

  def _createFirstUser(self, add_extensions=False):
    """
    Create first user, whose CSR is automatically signed.
    """
    basename = self._getBaseName()
    user_key_path = self._createPrivateKey(basename)
    csr_builder = self._getBasicCSRBuilder()
    if add_extensions:
      csr_builder = csr_builder.add_extension(
        x509.CertificatePolicies([
          x509.PolicyInformation(
            x509.oid.ObjectIdentifier(NOT_CAUCASE_OID),
            None,
          )
        ]),
        critical=False,
      )
    csr_path = self._finalizeCSR(
      basename,
      user_key_path,
      csr_builder,
    )
    out, = self._runClient(
      '--mode', 'user',
      '--send-csr', csr_path,
    ).splitlines()
    csr_id, csr_path_out = out.split()
    # Sanity check output
    self.assertEqual(csr_path, csr_path_out)
    int(csr_id)
    self.assertRaises(TypeError, utils.getCert, user_key_path)
    self._runClient(
      '--mode', 'user',
      '--get-crt', csr_id, user_key_path,
    )
    # Does not raise anymore, we have a certificate
    utils.getCert(user_key_path)
    return user_key_path

  def _createAndApproveCertificate(self, user_key_path, mode):
    """
    Create a CSR, submit it, approve it and retrieve the certificate.
    """
    basename = self._getBaseName()
    key_path = self._createPrivateKey(basename)
    csr_path = self._createBasicCSR(basename, key_path)
    out, = self._runClient(
      '--mode', mode,
      '--send-csr', csr_path,
    ).splitlines()
    csr_id, csr_path_out = out.split()
    # Sanity check output
    self.assertEqual(csr_path, csr_path_out)
    int(csr_id)
    self.assertRaises(TypeError, utils.getCert, key_path)
    out = self._runClient(
      '--mode', mode,
      '--get-crt', csr_id, key_path,
    ).splitlines()
    self.assertRaises(TypeError, utils.getCert, key_path)
    self.assertEqual([csr_id + ' CSR still pending'], out)
    csr2_path = csr_path + '.2'
    self._runClient(
      '--mode', mode,
      '--get-csr', csr_id, csr2_path,
    )
    with open(csr_path, 'rb') as csr_file, open(csr2_path, 'rb') as csr2_file:
      self.assertEqual(csr_file.read(), csr2_file.read())
    # Sign using user cert
    # Note: assuming user does not know the csr_id and keeps their own copy of
    # issued certificates.
    out = self._runClient(
      '--mode', mode,
      '--user-key', user_key_path,
      '--list-csr',
    ).splitlines()
    self.assertEqual([csr_id], [x.split(None, 1)[0] for x in out[2:-1]])
    self.assertRaises(
      CaucaseError,
      self._runClient,
      '--mode', mode,
      '--user-key', user_key_path,
      '--sign-csr', str(int(csr_id) + 1),
    )
    out = self._runClient(
      '--mode', mode,
      '--user-key', user_key_path,
      '--sign-csr', csr_id,
    )
    self.assertRaises(
      CaucaseError,
      self._runClient,
      '--mode', mode,
      '--user-key', user_key_path,
      '--sign-csr', csr_id,
    )
    # Now requester can get their certificate
    out, = self._runClient(
      '--mode', mode,
      '--get-crt', csr_id, key_path,
    ).splitlines()
    # Does not raise anymore, we have a certificate
    utils.getCert(user_key_path)
    return key_path

  def testBasicUsage(self):
    """
    Everybody plays by the rules (which includes trying to access when
    revoked).
    """
    self.assertFalse(os.path.exists(self._client_ca_crt))
    self.assertFalse(os.path.exists(self._client_crl))
    self.assertFalse(os.path.exists(self._client_user_ca_crt))
    self.assertFalse(os.path.exists(self._client_user_crl))
    # Running client creates CAS files (service CA & service CRL)
    self._runClient()
    self.assertTrue(os.path.exists(self._client_ca_crt))
    self.assertTrue(os.path.exists(self._client_crl))
    self.assertFalse(os.path.exists(self._client_user_ca_crt))
    self.assertFalse(os.path.exists(self._client_user_crl))
    # Running in "user" mode also created the CAU CA, but not the CAU CRL
    self._runClient('--mode', 'user')
    self.assertTrue(os.path.exists(self._client_ca_crt))
    self.assertTrue(os.path.exists(self._client_crl))
    self.assertTrue(os.path.exists(self._client_user_ca_crt))
    self.assertFalse(os.path.exists(self._client_user_crl))

    cas_crt_list = [
      utils.load_ca_certificate(x)
      for x in utils.getCertList(self._client_ca_crt)
    ]
    cau_crt_list = [
      utils.load_ca_certificate(x)
      for x in utils.getCertList(self._client_user_ca_crt)
    ]
    # No CA renewal happened yet
    self.assertEqual(len(cas_crt_list), 1)
    self.assertEqual(len(cau_crt_list), 1)

    # Get a user key pair
    user_key_path = self._createFirstUser()
    # It must have been auto-signed
    self.assertTrue(utils.isCertificateAutoSigned(utils.load_certificate(
      # utils.getCert(user_key_path) does not raise anymore
      utils.getCert(user_key_path),
      cau_crt_list,
      None,
    )))

    # Get a not-auto-approved service crt (the first auto-approved one was for
    # the http server itself)
    service_key = self._createAndApproveCertificate(
      user_key_path,
      'service',
    )
    self.assertFalse(utils.isCertificateAutoSigned(utils.load_certificate(
      utils.getCert(service_key),
      cas_crt_list,
      None,
    )))

    # Get a not-auto-approved user crt
    user2_key_path = self._createAndApproveCertificate(
      user_key_path,
      'user',
    )
    self.assertFalse(utils.isCertificateAutoSigned(utils.load_certificate(
      utils.getCert(user2_key_path),
      cau_crt_list,
      None,
    )))
    # It can itself sign certificates...
    service2_key_path = self._createAndApproveCertificate(
      user2_key_path,
      'service',
    )
    user3_key_path = self._createAndApproveCertificate(
      user2_key_path,
      'user',
    )
    self._runClient(
      '--user-key', user2_key_path,
      '--list-csr',
    )
    self._runClient(
      '--mode', 'user',
      '--user-key', user2_key_path,
      '--list-csr',
    )
    # ...until it gets revoked
    self._runClient(
      '--user-key', user_key_path,
      '--mode', 'user',
      '--revoke-other-crt', user2_key_path,
      '--update-user',
    )
    self.assertRaises(
      CaucaseError,
      self._createAndApproveCertificate,
      user2_key_path,
      'service',
    )
    self.assertRaises(
      CaucaseError,
      self._createAndApproveCertificate,
      user2_key_path,
      'user',
    )
    self.assertRaises(
      CaucaseError,
      self._runClient,
      '--user-key', user2_key_path,
      '--list-csr',
    )
    self.assertRaises(
      CaucaseError,
      self._runClient,
      '--mode', 'user',
      '--user-key', user2_key_path,
      '--list-csr',
    )
    # But the user it approved still works...
    self._runClient(
      '--user-key', user3_key_path,
      '--list-csr',
    )
    # ...until it revokes itself
    self._runClient(
      '--mode', 'user',
      '--user-key', user3_key_path,
      '--revoke-serial', str(
        utils.load_certificate(
          utils.getCert(user3_key_path),
          cau_crt_list,
          None,
        ).serial_number,
      )
    )
    self.assertRaises(
      CaucaseError,
      self._runClient,
      '--user-key', user3_key_path,
      '--list-csr',
    )
    # And the service it approved works too
    service2_crt_before, service2_key_before, _ = utils.getKeyPair(
      service2_key_path,
    )
    self._runClient(
      # 100 days is longer than certificate life, so it will be immediately
      # renewed.
      '--threshold', '100',
      '--renew-crt', service2_key_path, '',
    )
    service2_crt_after, service2_key_after, _ = utils.getKeyPair(
      service2_key_path,
    )
    # Certificate and key were renewed...
    self.assertNotEqual(service2_crt_before, service2_crt_after)
    self.assertNotEqual(service2_key_before, service2_key_after)
    # ...and not just swapped
    self.assertNotEqual(service2_crt_before, service2_key_after)
    self.assertNotEqual(service2_key_before, service2_crt_after)
    # It can revoke itself...
    self._runClient(
      '--revoke-crt', service2_key_path, '',
    )
    # ...and then it cannot renew itself any more...
    self.assertRaises(
      CaucaseError,
      self._runClient,
      '--threshold', '100',
      '--renew-crt', service2_key_path, '',
    )
    service2_crt_after2, service2_key_after2, _ = utils.getKeyPair(
      service2_key_path,
    )
    # and crt & key did not change
    self.assertEqual(service2_crt_after, service2_crt_after2)
    self.assertEqual(service2_key_after, service2_key_after2)
    # revoking again one's own certificate fails
    self.assertRaises(
      CaucaseError,
      self._runClient,
      '--revoke-crt', service2_key_path, '',
    )
    # as does revoking with an authenticated user
    self.assertRaises(
      CaucaseError,
      self._runClient,
      '--user-key', user_key_path,
      '--revoke-other-crt', service2_key_path,
    )
    # and revoking by serial
    self.assertRaises(
      CaucaseError,
      self._runClient,
      '--user-key', user_key_path,
      '--revoke-serial', str(
        utils.load_certificate(
          utils.getCert(service2_key_path),
          cas_crt_list,
          None,
        ).serial_number,
      ),
    )

    # Rejecting a CSR
    basename = self._getBaseName()
    key_path = self._createPrivateKey(basename)
    csr_path = self._createBasicCSR(basename, key_path)
    out, = self._runClient(
      '--send-csr', csr_path,
    ).splitlines()
    csr_id, csr_path_out = out.split()
    # Sanity check output
    self.assertEqual(csr_path, csr_path_out)
    int(csr_id)
    self.assertRaises(TypeError, utils.getCert, key_path)
    out = self._runClient(
      '--get-crt', csr_id, key_path,
    ).splitlines()
    self.assertRaises(TypeError, utils.getCert, key_path)
    self.assertEqual([csr_id + ' CSR still pending'], out)
    out = self._runClient(
      '--user-key', user_key_path,
      '--reject-csr', csr_id,
    ).splitlines()
    # Re-rejecting fails
    self.assertRaises(
      CaucaseError,
      self._runClient,
      '--user-key', user_key_path,
      '--reject-csr', csr_id,
    )
    # like rejecting a non-existing crt
    self.assertRaises(
      CaucaseError,
      self._runClient,
      '--user-key', user_key_path,
      '--reject-csr', str(int(csr_id) + 1),
    )
    out = self._runClient(
      '--get-crt', csr_id, key_path,
    ).splitlines()
    self.assertRaises(TypeError, utils.getCert, key_path)
    self.assertEqual([
      csr_id + ' not found - maybe CSR was rejected ?'
    ], out)

  def testBadCSR(self):
    """
    Submitting an invalid CSR.

    Requires bypassing cli, as it does its own checks.
    """
    client = CaucaseClient(self._caucase_url + '/cas')
    try:
      client.createCertificateSigningRequest('Not actually a CSR')
    except CaucaseError as e:
      self.assertEqual(e.args[0], 400, e)
    else: # pragma: no cover
      raise AssertionError('Did not raise CaucaseError(400, ...)')

  def testUpdateUser(self):
    """
    Verify that CAU certificate and revocation list are created when the
    (rarely needed) --update-user option is given.
    """
    self.assertFalse(os.path.exists(self._client_ca_crt))
    self.assertFalse(os.path.exists(self._client_crl))
    self.assertFalse(os.path.exists(self._client_user_ca_crt))
    self.assertFalse(os.path.exists(self._client_user_crl))
    self._runClient('--update-user')
    self.assertTrue(os.path.exists(self._client_ca_crt))
    self.assertTrue(os.path.exists(self._client_crl))
    self.assertTrue(os.path.exists(self._client_user_ca_crt))
    self.assertTrue(os.path.exists(self._client_user_crl))

  def testMaxCSR(self):
    """
    Verify that the number of pending CSR is properly constrained.
    """
    csr_list = []
    def assertCanSend(count):
      """
      Check that caucased accepts <count> CSR, and rejects the next one.
      Appends the data of created CSRs (csr_id and csr_path) to csr_list.
      """
      for _ in xrange(count):
        basename = self._getBaseName()
        csr_path = self._createBasicCSR(
          basename,
          self._createPrivateKey(basename),
        )
        out, = self._runClient('--send-csr', csr_path).splitlines()
        csr_id, _ = out.split()
        csr_list.append((csr_id, csr_path))
      basename = self._getBaseName()
      bad_csr_path = self._createBasicCSR(
        basename,
        self._createPrivateKey(basename),
      )
      self.assertRaises(
        CaucaseError,
        self._runClient,
        '--send-csr',
        bad_csr_path,
      )

    user_key_path = self._createFirstUser()
    self._stopServer()
    self._startServer(
      '--service-max-csr', '5',
    )
    assertCanSend(5)
    # But resubmitting one of the accepted ones is still fine
    _, csr_path = csr_list[0]
    self._runClient('--send-csr', csr_path)

    # Accepted certificates do not count towards the total, even if not
    # retrieved by owner
    csr_id, csr_path = csr_list.pop()
    self._runClient(
      '--user-key', user_key_path,
      '--sign-csr', csr_id,
    )
    assertCanSend(1)
    # Rejected certificates do not count towards the total.

    csr_id, _ = csr_list.pop()
    self._runClient(
      '--user-key', user_key_path,
      '--reject-csr', csr_id,
    )
    assertCanSend(1)

  def testLockAutoSignAmount(self):
    """
    Verify that auto-approve limit freezing works.
    """
    self._stopServer()
    self._startServer(
      '--user-auto-approve-count', '2',
      '--lock-auto-approve-count',
    )
    self._stopServer()
    self._startServer(
      '--user-auto-approve-count', '3',
    )
    self._createFirstUser()
    self._createFirstUser()
    self.assertRaises(TypeError, self._createFirstUser)
    self._stopServer()
    self._startServer(
      '--user-auto-approve-count', '3',
      '--lock-auto-approve-count',
    )
    self.assertRaises(TypeError, self._createFirstUser)

  def testCSRFiltering(self):
    """
    Verify that requester cannot get any extension or extension value they
    ask for. Caucase has to protect itself to be trustworthy, but also to let
    some liberty to requester.
    """
    def checkCRT(key_path):
      """
      Verify key_path to contain exactly one certificate, itself containing
      all expected extensions.
      """
      crt = utils.load_certificate(
        utils.getCert(key_path),
        cas_crt_list,
        None,
      )
      # CA-only extension, must not be present in certificate
      self.assertRaises(
        x509.ExtensionNotFound,
        crt.extensions.get_extension_for_class,
        x509.NameConstraints,
      )
      for expected_value in [
        expected_key_usage,
        expected_extended_usage,
        expected_alt_name,
        expected_policies,
        expected_basic_constraints,
      ]:
        extension = crt.extensions.get_extension_for_class(
          expected_value.__class__,
        )
        self.assertEqual(
          extension.value,
          expected_value,
        )
        self.assertTrue(extension.critical)
    requested_key_usage = x509.KeyUsage(
      # pylint: disable=bad-whitespace
      digital_signature =True,
      content_commitment=True,
      key_encipherment  =True,
      data_encipherment =True,
      key_agreement     =True,
      key_cert_sign     =True,
      crl_sign          =True,
      encipher_only     =True,
      decipher_only     =False,
      # pylint: enable=bad-whitespace
    )
    expected_key_usage = x509.KeyUsage(
      # pylint: disable=bad-whitespace
      digital_signature =True,
      content_commitment=True,
      key_encipherment  =True,
      data_encipherment =True,
      key_agreement     =True,
      key_cert_sign     =False,
      crl_sign          =False,
      encipher_only     =True,
      decipher_only     =False,
      # pylint: enable=bad-whitespace
    )
    requested_extended_usage = x509.ExtendedKeyUsage([
      x509.oid.ExtendedKeyUsageOID.OCSP_SIGNING,
      x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
    ])
    expected_extended_usage = x509.ExtendedKeyUsage([
      x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
    ])
    requested_alt_name = expected_alt_name = x509.SubjectAlternativeName([
      x509.RFC822Name(u'nobody@example.com'),
      x509.DNSName(u'example.com'),
      x509.UniformResourceIdentifier(u'https://example.com/a/b/c'),
      x509.IPAddress(ipaddress.IPv4Address(u'127.0.0.1')),
      x509.IPAddress(ipaddress.IPv6Address(u'::1')),
      x509.IPAddress(ipaddress.IPv4Network(u'127.0.0.0/8')),
      x509.IPAddress(ipaddress.IPv6Network(u'::/64')),
    ])
    requested_policies = x509.CertificatePolicies([
      x509.PolicyInformation(
        x509.oid.ObjectIdentifier(utils.CAUCASE_OID_RESERVED),
        None,
      ),
      x509.PolicyInformation(
        x509.oid.ObjectIdentifier(NOT_CAUCASE_OID),
        None,
      ),
    ])
    expected_policies = x509.CertificatePolicies([
      x509.PolicyInformation(
        x509.oid.ObjectIdentifier(NOT_CAUCASE_OID),
        None,
      ),
    ])
    requested_basic_constraints = x509.BasicConstraints(
      ca=True,
      path_length=42,
    )
    expected_basic_constraints = x509.BasicConstraints(
      ca=False,
      path_length=None,
    )

    # Check stored CSR filtering
    user_key_path = self._createFirstUser(add_extensions=True)
    basename = self._getBaseName()
    key_path = self._createPrivateKey(basename)
    requested_csr_path = self._finalizeCSR(
      basename,
      key_path,
      self._getBasicCSRBuilder(
      ).add_extension(requested_key_usage, critical=True,
      ).add_extension(requested_extended_usage, critical=True,
      ).add_extension(requested_alt_name, critical=True,
      ).add_extension(requested_policies, critical=True,
      ).add_extension(requested_basic_constraints, critical=True,
      ).add_extension(
        x509.NameConstraints([x509.DNSName(u'com')], None),
        critical=True,
      ),
    )
    out, = self._runClient(
      '--send-csr', requested_csr_path,
    ).splitlines()
    csr_id, _ = out.split()
    int(csr_id)
    self._runClient(
      '--user-key', user_key_path,
      '--sign-csr', csr_id,
    )
    self._runClient(
      '--get-crt', csr_id, key_path,
    )
    cas_crt_list = [
      utils.load_ca_certificate(x)
      for x in utils.getCertList(self._client_ca_crt)
    ]
    cau_crt_list = [
      utils.load_ca_certificate(x)
      for x in utils.getCertList(self._client_user_ca_crt)
    ]
    checkCRT(key_path)

    # Check renewed CRT filtering does not alter clean signed certificate
    # content (especially, caucase auto-signed flag must not appear).
    with open(key_path, 'rb') as key_file:
      before_key = key_file.read()
    self._runClient(
      '--threshold', '100',
      '--renew-crt', key_path, '',
    )
    with open(key_path, 'rb') as key_file:
      after_key = key_file.read()
    assert before_key != after_key
    checkCRT(key_path)

    # Check content of auto-issued user certificate
    user_crt = utils.load_certificate(
      utils.getCert(user_key_path),
      cau_crt_list,
      None,
    )
    user_certificate_policies = user_crt.extensions.get_extension_for_class(
      x509.CertificatePolicies,
    )
    self.assertEqual(
      user_certificate_policies.value,
      x509.CertificatePolicies([
        x509.PolicyInformation(
          x509.oid.ObjectIdentifier(NOT_CAUCASE_OID),
          None,
        ),
        utils.CAUCASE_POLICY_INFORMATION_AUTO_SIGNED,
      ]),
    )
    self.assertFalse(user_certificate_policies.critical)

    # Check template CSR: must be taken into account, but it also gets
    # filtered.
    basename2 = self._getBaseName()
    key_path2 = self._createPrivateKey(basename2)
    out, = self._runClient(
      '--send-csr', self._finalizeCSR(
        basename2,
        key_path2,
        self._getBasicCSRBuilder(),
      ),
    ).splitlines()
    csr_id, _ = out.split()
    int(csr_id)
    self._runClient(
      '--user-key', user_key_path,
      '--sign-csr-with', csr_id, requested_csr_path,
    )
    self._runClient(
      '--get-crt', csr_id, key_path2,
    )
    checkCRT(key_path2)

  def testCACertRenewal(self):
    """
    Exercise CA certificate rollout procedure.
    """
    user_key_path = self._createFirstUser()
    cau_crt, = [
      utils.load_ca_certificate(x)
      for x in utils.getCertList(self._client_user_ca_crt)
    ]
    self._stopServer()
    # CA expires in 100 days: longer than one certificate life,
    # but shorter than two. A new CA must be generated and distributed,
    # but not used for new signatures yet.
    new_cau_crt_pem = self._setCACertificateRemainingLifeTime(
      'user',
      cau_crt.serial_number,
      datetime.timedelta(100, 0),
    )
    # As we will use this crt as trust anchor, we must make the client believe
    # it knew it all along.
    with open(self._client_user_ca_crt, 'wb') as client_user_ca_crt_file:
      client_user_ca_crt_file.write(new_cau_crt_pem)
    self._startServer()
    new_user_key = self._createAndApproveCertificate(
      user_key_path,
      'user',
    )
    # Must not raise: we are signed with the "old" ca.
    utils.load_certificate(
      utils.getCert(new_user_key),
      [cau_crt],
      None,
    )
    # We must now know the new CA
    cau_crt_list = [
      utils.load_ca_certificate(x)
      for x in utils.getCertList(self._client_user_ca_crt)
    ]
    new_cau_crt, = [
      x for x in cau_crt_list
      if x.serial_number != cau_crt.serial_number
    ]
    self._stopServer()
    # New CA now exists for 100 days: longer than one certificate life.
    # It may (must) be used for new signatures.
    self._setCACertificateRemainingLifeTime(
      'user',
      new_cau_crt.serial_number,
      new_cau_crt.not_valid_after - new_cau_crt.not_valid_before -
      datetime.timedelta(100, 0),
    )
    self._startServer()
    self._runClient(
      '--mode', 'user',
      # 100 days is longer than certificate life, so it will be immediately
      # renewed.
      '--threshold', '100',
      '--renew-crt', new_user_key, '',
    )
    self.assertRaises(
      exceptions.CertificateVerificationError,
      utils.load_certificate,
      utils.getCert(new_user_key),
      [cau_crt],
      None,
    )
    utils.load_certificate(
      utils.getCert(new_user_key),
      cau_crt_list,
      None,
    )

  def testCaucasedCertRenewal(self):
    """
    Exercise caucased internal certificate renewal procedure.
    """
    user_key_path = self._createFirstUser()
    self._stopServer()
    # If server certificate is deleted, it gets re-created, even it CAS
    # reached its certificate auto-approval limit.
    os.unlink(self._server_key)
    self._startServer()
    if not retry(lambda: os.path.exists(self._server_key)): # pragma: no cover
      raise AssertionError('%r was not recreated within 1 second' % (
        self._server_key,
      ))
    # But user still trusts the server
    self._runClient(
      '--mode', 'user',
      # 100 days is longer than certificate life, so it will be immediately
      # renewed.
      '--threshold', '100',
      '--renew-crt', user_key_path, '',
    )
    # Server certificate will expire in 20 days, the key must be renewed
    # (but we have to peek at HTTP CAS private key, cover your eyes)
    (http_cas_key, ), = sqlite3.connect(
      self._server_db,
    ).cursor().execute(
      'SELECT key FROM http_casca',
    ).fetchall()

    self._stopServer()
    crt_pem, key_pem, ca_crt_pem = utils.getCertKeyAndCACert(
      self._server_key,
      crl=None,
    )
    with open(self._server_key, 'wb') as server_key_file:
      server_key_file.write(key_pem)
      server_key_file.write(utils.dump_certificate(
        self._setCertificateRemainingLifeTime(
          key=utils.load_privatekey(utils.toBytes(http_cas_key)),
          crt=utils.load_certificate(
            crt_pem,
            [
              utils.load_ca_certificate(ca_crt_pem),
            ],
            None,
          ),
          delta=datetime.timedelta(20, 0)
        )
      ))
      server_key_file.write(ca_crt_pem)
    def readServerKey():
      """
      Read server key from file.
      """
      with open(self._server_key, 'rb') as server_key_file:
        return server_key_file.read()
    reference_server_key = readServerKey()
    self._startServer()
    if not retry(
      lambda: readServerKey() != reference_server_key,
    ): # pragma: no cover
      raise AssertionError('Server did not renew its key pair within 1 second')
    # But user still trusts the server
    self._runClient(
      '--mode', 'user',
      # 100 days is longer than certificate life, so it will be immediately
      # renewed.
      '--threshold', '100',
      '--renew-crt', user_key_path, '',
    )

  def testCORSTokenManager(self):
    """
    Test key expiration and onNewKey invocation.
    """
    new_key_list = []
    old_key_value = '\x00' * 32
    wsgi.CORSTokenManager(
      secret_list=(
        # A secret which is still valid, but old enough to not be used.
        (time.time() + A_YEAR_IN_SECONDS // 2 - 86400, old_key_value),
      ),
      onNewKey=new_key_list.append,
    ).sign('')
    # pylint: disable=unbalanced-tuple-unpacking
    ((_, old_key), (_, _)), = new_key_list
    # pylint: enable=unbalanced-tuple-unpacking
    self.assertEqual(old_key, old_key_value)

  def testWSGI(self):
    """
    Test wsgi class reaction to malformed requests.

    For tests which are not accessible through the client module (as it tries
    to only produce valid requests).
    """
    self._runClient('--mode', 'user', '--update-user')
    cau_list = [
      utils.load_ca_certificate(x)
      for x in utils.getCertList(self._client_user_ca_crt)
    ]
    with open(self._client_user_crl, 'rb') as client_user_crl_file:
      cau_crl = client_user_crl_file.read()
    class DummyCAU(object):
      """
      Mock CAU.
      """
      digest_list = ['sha256']

      @staticmethod
      def getCACertificateList():
        """
        Return cau ca list.
        """
        return cau_list

      @staticmethod
      def getCACertificate():
        """
        Return a dummy string as CA certificate
        """
        return b'notreallyPEM'

      @staticmethod
      def getCertificateRevocationList():
        """
        Return cau crl.
        """
        return cau_crl

      @staticmethod
      def appendCertificateSigningRequest(_):
        """
        Raise to exercise the "unexpected exception" code path in WSGI.
        """
        raise ValueError('Some generic exception')

      @staticmethod
      def _placeholder(_): # pragma: no cover
        """
        Placeholder methods, for when method lookup happens before noticing
        issues in the query.
        """
        raise AssertionError('code should fail before actually calling this')

      getCertificateSigningRequest = _placeholder
      getCertificate = _placeholder

    server_name = u'caucase.example.com'
    server_http_port = 8000
    server_https_port = server_http_port + 1
    application = wsgi.Application(
      DummyCAU(),
      None,
      'http://%s:%i' % (server_name, server_http_port),
      'https://%s:%i' % (server_name, server_https_port),
      wsgi.CORSTokenManager(),
    )
    def request(environ):
      """
      Non-standard shorthand for invoking the WSGI application.
      """
      environ.setdefault('wsgi.errors', self.caucase_test_output)
      environ.setdefault('wsgi.url_scheme', 'http')
      environ.setdefault('SERVER_NAME', server_name)
      environ.setdefault('SERVER_PORT', str(server_http_port))
      start_response_list = []
      body = list(application(
        environ,
        lambda status, header_list: start_response_list.append(
          (status, header_list),
        ),
      ))
      # pylint: disable=unbalanced-tuple-unpacking
      (status, header_list), = start_response_list
      # pylint: enable=unbalanced-tuple-unpacking
      status, reason = status.split(' ', 1)
      header_dict = {}
      for key, value in header_list:
        if key in header_dict: # pragma: no cover
          value = header_dict[key] + ',' + value
        header_dict[key] = value
      return int(status), reason, header_dict, b''.join(body)
    UNAUTHORISED_STATUS = 401

    HATEOAS_HTTP_PREFIX = u"http://%s:%i/base/path" % (
      server_name,
      server_http_port,
    )
    HATEOAS_HTTPS_PREFIX = u"https://%s:%i/base/path" % (
      server_name,
      server_https_port,
    )
    status, _, header_dict, body = request({
      'SCRIPT_NAME': '/base/path',
      'REQUEST_METHOD': 'GET',
    })
    self.maxDiff = None
    self.assertEqual(status, 200)
    self.assertEqual(header_dict['Content-Type'], 'application/hal+json')
    self.assertEqual(json.loads(body), {
      u"_links": {
        u"getCAUHAL": {
          u"href": HATEOAS_HTTP_PREFIX + u"/cau",
          u"title": u"cau",
        },
        u"self": {
          u"href": HATEOAS_HTTP_PREFIX,
        },
        u"getCASHAL": {
          u"href": HATEOAS_HTTP_PREFIX + u"/cas",
          u"title": u"cas",
        },
      },
    })
    status, _, header_dict, body = request({
      'SCRIPT_NAME': '/base/path',
      'PATH_INFO': '/cau/',
      'REQUEST_METHOD': 'GET',
    })
    self.assertEqual(status, 200)
    self.assertEqual(header_dict['Content-Type'], 'application/hal+json')
    self.assertEqual(json.loads(body), {
      u"_actions": {
        u"createCertificate": {
          u"href": HATEOAS_HTTPS_PREFIX + u"/cau/crt/{+crt_id}",
          u"method": u"PUT",
          u"templated": True,
          u"title": u"Accept pending certificate signing request",
        },
        u"renewCertificate": {
          u"href": HATEOAS_HTTP_PREFIX + u"/cau/crt/renew",
          u"method": u"PUT",
          u"title": u"Renew a certificate",
        },
        u"revokeCertificate": {
          u"href": HATEOAS_HTTP_PREFIX + u"/cau/crt/revoke",
          u"method": u"PUT",
          u"title": u"Revoke a certificate",
        },
        u"createCertificateSigningRequest": {
          u"href": HATEOAS_HTTP_PREFIX + u"/cau/csr",
          u"method": u"PUT",
          u"title": u"Request a new certificate signature.",
        },
        u"deletePendingCertificateRequest": {
          u"href": HATEOAS_HTTPS_PREFIX + u"/cau/csr/{+csr_id}",
          u"method": u"DELETE",
          u"templated": True,
          u"title": u"Reject a pending certificate signing request.",
        },
      },
      u"_links": {
        u"getCertificateRevocationList": {
          u"href": HATEOAS_HTTP_PREFIX + u"/cau/crl",
          u"title": u"Retrieve latest certificate revocation list.",
        },
        u"getCACertificate": {
          u"href": HATEOAS_HTTP_PREFIX + u"/cau/crt/ca.crt.pem",
          u"title": u"Retrieve current CA certificate.",
        },
        u"self": {
          u"href": HATEOAS_HTTP_PREFIX + u"/cau",
        },
        u"getCertificate": {
          u"href": HATEOAS_HTTP_PREFIX + u"/cau/crt/{+csr_id}",
          u"templated": True,
          u"title": u"Retrieve a signed certificate.",
        },
        u"getPendingCertificateRequestList": {
          u"href": HATEOAS_HTTPS_PREFIX + u"/cau/csr",
          u"title": u"List pending certificate signing requests.",
        },
        u"getCACertificateChain": {
          u"href": HATEOAS_HTTP_PREFIX + u"/cau/crt/ca.crt.json",
          u"title": u"Retrieve current CA certificate trust chain.",
        },
        u"getCertificateSigningRequest": {
          u"href": HATEOAS_HTTP_PREFIX + u"/cau/csr/{+csr_id}",
          u"templated": True,
          u"title": u"Retrieve a pending certificate signing request.",
        },
        u"home": {
          u"href": HATEOAS_HTTP_PREFIX,
        },
      },
    })
    self.assertEqual(request({
      'PATH_INFO': '/foo/bar',
      'REQUEST_METHOD': 'GET',
    })[0], 404)
    self.assertEqual(request({
      'PATH_INFO': '/cau/__init__',
      'REQUEST_METHOD': 'GET',
    })[0], 404)
    self.assertEqual(request({
      'PATH_INFO': '/cau/does_not_exist',
      'REQUEST_METHOD': 'GET',
    })[0], 404)

    self.assertEqual(request({
      'PATH_INFO': '/cau/crl/123',
      'REQUEST_METHOD': 'GET',
    })[0], 404)

    min_date = int(time.time())
    status, _, header_dict, _ = request({
      'PATH_INFO': '/cau/crl',
      'REQUEST_METHOD': 'PUT',
    })
    max_date = int(time.time())
    self.assertEqual(status, 405)
    self.assertItemsEqual(
      [x.strip() for x in header_dict['Allow'].split(',')],
      ['GET', 'OPTIONS'],
    )
    response_date = utils.IMFfixdate2timestamp(header_dict['Date'])
    self.assertGreaterEqual(response_date, min_date)
    self.assertLessEqual(response_date, max_date)

    self.assertEqual(request({
      'PATH_INFO': '/cau/csr/123/456',
      'REQUEST_METHOD': 'GET',
    })[0], 404)
    self.assertEqual(request({
      'PATH_INFO': '/cau/csr/123',
      'REQUEST_METHOD': 'POST',
    })[0], 405)
    self.assertEqual(request({
      'PATH_INFO': '/cau/csr/a',
      'REQUEST_METHOD': 'GET',
    })[0], 400)
    self.assertEqual(request({
      'PATH_INFO': '/cau/csr',
      'REQUEST_METHOD': 'GET',
    })[0], UNAUTHORISED_STATUS)
    self.assertEqual(request({
      'PATH_INFO': '/cau/csr/123',
      'REQUEST_METHOD': 'PUT',
    })[0], 404)
    self.assertEqual(request({
      'PATH_INFO': '/cau/csr',
      'REQUEST_METHOD': 'PUT',
      'wsgi.input': StringIO(),
    })[0], 500)
    self.assertEqual(request({
      'PATH_INFO': '/cau/csr',
      'REQUEST_METHOD': 'DELETE',
    })[0], 404)
    self.assertEqual(request({
      'PATH_INFO': '/cau/csr/123/456',
      'REQUEST_METHOD': 'DELETE',
    })[0], 404)
    self.assertEqual(request({
      'PATH_INFO': '/cau/csr/123',
      'REQUEST_METHOD': 'DELETE',
    })[0], UNAUTHORISED_STATUS)

    self.assertEqual(request({
      'PATH_INFO': '/cau/crt',
      'REQUEST_METHOD': 'GET',
    })[0], 404)
    self.assertEqual(request({
      'PATH_INFO': '/cau/crt/123/456',
      'REQUEST_METHOD': 'GET',
    })[0], 404)
    self.assertEqual(request({
      'PATH_INFO': '/cau/crt/a',
      'REQUEST_METHOD': 'GET',
    })[0], 400)
    self.assertEqual(request({
      'PATH_INFO': '/cau/crt/renew',
      'REQUEST_METHOD': 'PUT',
      'CONTENT_TYPE': 'text/plain',
    })[0], 400)
    self.assertEqual(request({
      'PATH_INFO': '/cau/crt/renew',
      'REQUEST_METHOD': 'PUT',
      'CONTENT_TYPE': 'application/json',
      'CONTENT_LENGTH': 'a',
      'wsgi.input': StringIO(),
    })[0], 400)
    self.assertEqual(request({
      'PATH_INFO': '/cau/crt/renew',
      'REQUEST_METHOD': 'PUT',
      'CONTENT_TYPE': 'application/json',
      'CONTENT_LENGTH': str(wsgi.MAX_BODY_LENGTH + 1),
      'wsgi.input': StringIO(),
    })[0], 413)
    self.assertEqual(request({
      'PATH_INFO': '/cau/crt/renew',
      'REQUEST_METHOD': 'PUT',
      'CONTENT_TYPE': 'application/json',
      'wsgi.input': StringIO(u'{'),
    })[0], 400)
    self.assertEqual(request({
      'PATH_INFO': '/cau/crt/revoke',
      'REQUEST_METHOD': 'PUT',
      'CONTENT_TYPE': 'application/json',
      'wsgi.input': StringIO(u'{"digest": null}'),
    })[0], UNAUTHORISED_STATUS)
    self.assertEqual(request({
      'PATH_INFO': '/cau/crt/revoke',
      'REQUEST_METHOD': 'PUT',
      'CONTENT_TYPE': 'application/json',
      'wsgi.input': StringIO(u'{"digest":"sha256","payload":""}'),
    })[0], 400)
    self.assertEqual(request({
      'PATH_INFO': '/cau/crt/a',
      'REQUEST_METHOD': 'PUT',
      'CONTENT_TYPE': 'text/plain',
      'wsgi.input': StringIO(u''),
    })[0], 400)
    self.assertEqual(request({
      'PATH_INFO': '/cau/crt/123',
      'REQUEST_METHOD': 'PUT',
      'CONTENT_TYPE': 'text/plain',
      'wsgi.input': StringIO(u''),
    })[0], UNAUTHORISED_STATUS)
    self.assertEqual(request({
      'PATH_INFO': '/cau/crt/123',
      'REQUEST_METHOD': 'PUT',
      'CONTENT_TYPE': 'text/plain',
      'wsgi.input': StringIO(u'foo'),
    })[0], 400)
    self.assertEqual(request({
      'PATH_INFO': '/cau/crt/123',
      'REQUEST_METHOD': 'POST',
    })[0], 405)

    # CORS
    cross_origin = 'https://example.com:443'
    # Non-CORS OPTIONS: success without CORS headers
    status, _, header_dict, _ = request({
      'PATH_INFO': '/',
      'REQUEST_METHOD': 'OPTIONS',
    })
    self.assertEqual(status, 204)
    self.assertNotIn(
      'Access-Control-Allow-Credentials',
      header_dict,
    )
    self.assertNotIn(
      'Access-Control-Allow-Origin',
      header_dict,
    )
    self.assertNotIn(
      'Vary',
      header_dict,
    )
    self.assertNotIn(
      'Access-Control-Allow-Methods',
      header_dict,
    )
    self.assertNotIn(
      'Access-Control-Allow-Headers',
      header_dict,
    )
    # All origins can access /
    status, _, header_dict, _ = request({
      'PATH_INFO': '/',
      'REQUEST_METHOD': 'OPTIONS',
      'HTTP_ORIGIN': cross_origin,
    })
    self.assertEqual(status, 204)
    self.assertEqual(
      header_dict['Access-Control-Allow-Credentials'],
      'true',
    )
    self.assertEqual(
      header_dict['Access-Control-Allow-Origin'],
      cross_origin,
    )
    self.assertEqual(
      header_dict['Vary'],
      'Origin',
    )
    self.assertItemsEqual(
      [
        x.strip()
        for x in header_dict['Access-Control-Allow-Methods'].split(',')
      ],
      ['GET', 'OPTIONS'],
    )
    self.assertItemsEqual(
      [
        x.strip()
        for x in header_dict['Access-Control-Allow-Headers'].split(',')
      ],
      [
        'Content-Type',
        'User-Agent',
      ],
    )
    # User confirmation is needed to GET /cau/crt/ca.crt.pem
    # ... OPTIONS succeeds and lists allowed methods
    status, _, header_dict, _ = request({
      'PATH_INFO': '/cau/crt/ca.crt.pem',
      'REQUEST_METHOD': 'OPTIONS',
      'HTTP_ORIGIN': cross_origin,
    })
    self.assertEqual(status, 204)
    self.assertItemsEqual(
      ['GET', 'OPTIONS'],
      [
        x.strip()
        for x in header_dict['Access-Control-Allow-Methods'].split(',')
      ],
    )
    # ... calling PUT tells Unauthorised with proper header
    status, _, header_dict, _ = request({
      'PATH_INFO': '/cau/crt/ca.crt.pem',
      'REQUEST_METHOD': 'GET',
      'HTTP_ORIGIN': cross_origin,
    })
    self.assertEqual(status, UNAUTHORISED_STATUS)
    self.assertEqual(
      header_dict['WWW-Authenticate'],
      'cors url=' + quote(
          'https://%s:%i/cors?' % (server_name, server_https_port) +
        urlencode([('origin', cross_origin)]) +
        '{&return}',
      ),
    )
    # ... it also fails cleanly when called with an invalid cookie
    self.assertEqual(
      request({
        'PATH_INFO': '/cau/crt/ca.crt.pem',
        'REQUEST_METHOD': 'GET',
        'HTTP_ORIGIN': cross_origin,
        'HTTP_COOKIE': 'cors=a',
      })[0],
      UNAUTHORISED_STATUS,
    )
    return_url = 'http://example.com/foo?d=<script>alert("boo !")</script>'
    # POST to /cors with origin is forbidden
    self.assertEqual(
      request({
        'wsgi.url_scheme': 'https',
        'PATH_INFO': '/cors',
        'QUERY_STRING': urlencode((
          ('origin', cross_origin),
          ('return', return_url),
        )),
        'REQUEST_METHOD': 'POST',
        'HTTP_ORIGIN': cross_origin,
      })[0],
      403,
    )
    # GET /cors on http redirects to https
    status, _, header_dict, _ = request({
      'wsgi.url_scheme': 'http',
      'PATH_INFO': '/cors',
      'QUERY_STRING': urlencode((
        ('origin', cross_origin),
        ('return', return_url),
      )),
      'REQUEST_METHOD': 'GET',
    })
    self.assertEqual(status, 302)
    self.assertTrue(
      header_dict['Location'].startswith('https://'),
      header_dict['Location'],
    )
    # GET /cors with missing arguments (here, "return") fails visibly
    self.assertEqual(
      request({
        'wsgi.url_scheme': 'https',
        'PATH_INFO': '/cors',
        'QUERY_STRING': urlencode((
          ('origin', cross_origin),
        )),
        'REQUEST_METHOD': 'GET',
      })[0],
      400,
    )
    # GET /cors return an html page with anti-clickjacking headers
    status, _, header_dict, body = request({
      'wsgi.url_scheme': 'https',
      'PATH_INFO': '/cors',
      'QUERY_STRING': urlencode((
        ('origin', cross_origin),
        ('return', return_url),
      )),
      'REQUEST_METHOD': 'GET',
    })
    self.assertEqual(status, 200)
    self.assertEqual(header_dict['Content-Type'], 'text/html')
    self.assertEqual(header_dict['X-Frame-Options'], 'DENY')
    self.assertEqual(
      header_dict['Content-Security-Policy'],
      "frame-ancestors 'none'",
    )
    assertHTMLNoScriptAlert(utils.toUnicode(body))
    # POST /cors sets cookie
    def getCORSPostEnvironment(kw=(), input_dict=(
      ('return_to', return_url),
      ('origin', cross_origin),
      ('grant', '1'),
    )):
      """
      Build "request"'s "environ" argument for CORS requests.
      """
      base_request_reader_dict = {
        'wsgi.url_scheme': 'https',
        'PATH_INFO': '/cors',
        'REQUEST_METHOD': 'POST',
        'CONTENT_TYPE': 'application/x-www-form-urlencoded',
        'wsgi.input': StringIO(utils.toUnicode(urlencode(input_dict))),
      }
      base_request_reader_dict.update(kw)
      return base_request_reader_dict
    def getCORSCookie(value):
      """
      Build CORS cookie with custome value
      """
      return SimpleCookie({'cors': json.dumps(value)})['cors'].OutputString()
    self.assertEqual(
      request(getCORSPostEnvironment(kw={'wsgi.url_scheme': 'http'}))[0],
      404,
    )
    self.assertEqual(
      request(getCORSPostEnvironment(kw={'CONTENT_TYPE': 'text/plain'}))[0],
      400,
    )
    self.assertEqual(
      request(getCORSPostEnvironment(
        input_dict={
          'return_to': return_url,
          'origin': cross_origin,
          # Missing "grant"
        },
      ))[0],
      400,
    )
    self.assertEqual(
      request(getCORSPostEnvironment(
        input_dict={
          'return_to': return_url,
          'origin': cross_origin,
          'grant': 'a', # Non-integer "grant"
        },
      ))[0],
      400,
    )
    status, _, header_dict, _ = request(getCORSPostEnvironment())
    self.assertEqual(status, 302)
    self.assertEqual(header_dict['Location'], return_url)
    good_token = json.loads(
      SimpleCookie(header_dict['Set-Cookie'])['cors'].value,
    )[cross_origin]
    # Recycling a valid token for another domain does not grant access
    status, _, header_dict, _ = request(getCORSPostEnvironment(
      input_dict={
        'return_to': 'http://example.org',
        'origin': 'http://example.org:80',
        'grant': '1',
      }
    ))
    self.assertEqual(status, 302)
    bad_token = json.loads(
      SimpleCookie(header_dict['Set-Cookie'])['cors'].value,
    )['http://example.org:80']
    status, _, header_dict, _ = request({
      'PATH_INFO': '/cau/crt/ca.crt.pem',
      'REQUEST_METHOD': 'GET',
      'HTTP_ORIGIN': cross_origin,
      'HTTP_COOKIE': getCORSCookie({
        cross_origin: bad_token,
      }),
    })
    self.assertEqual(status, UNAUTHORISED_STATUS)
    self.assertEqual(
      SimpleCookie(header_dict['Set-Cookie'])['cors'].value,
      '{}',
    )
    # Accessing with invalid token fails
    head, body, _ = good_token.split('.')
    _, _, signature = bad_token.split('.')
    status, _, header_dict, _ = request({
      'PATH_INFO': '/cau/crt/ca.crt.pem',
      'REQUEST_METHOD': 'GET',
      'HTTP_ORIGIN': cross_origin,
      'HTTP_COOKIE': getCORSCookie({
        cross_origin: '%s.%s.%s' % (
          head,
          body,
          signature,
        ),
      }),
    })
    self.assertEqual(status, UNAUTHORISED_STATUS)
    self.assertEqual(
      SimpleCookie(header_dict['Set-Cookie'])['cors'].value,
      '{}',
    )
    # Accessing with valid token works
    status, _, header_dict, _ = request({
      'PATH_INFO': '/cau/crt/ca.crt.pem',
      'REQUEST_METHOD': 'GET',
      'HTTP_ORIGIN': cross_origin,
      'HTTP_COOKIE': getCORSCookie({
        cross_origin: good_token,
      }),
    })
    self.assertEqual(status, 200)
    self.assertItemsEqual(
      [
        x.strip()
        for x in header_dict[
          'Access-Control-Expose-Headers'
        ].split(',')
      ],
      [
        'Location',
        'WWW-Authenticate',
      ],
    )

  def testProbe(self):
    """
    Exercise caucase-probe command.
    """
    cli.probe([self._caucase_url])

  def testBackup(self):
    """
    Exercise backup generation and restoration.
    """
    backup_glob = os.path.join(self._server_backup_path, '*.sql.caucased')
    user_key_path = self._createFirstUser()
    user2_key_path = self._createAndApproveCertificate(
      user_key_path,
      'user',
    )
    # user2 sacrifice their private key, and prepare its replacement
    basename = self._getBaseName()
    user2_new_key_path = self._createPrivateKey(basename)
    user2_new_csr_path = self._createBasicCSR(basename, user2_new_key_path)

    # Restart caucased to not have to wait for next backup deadline
    self._stopServer()
    # Note: backup could have triggered between first and second user's key
    # creation. We need it to be signed by both keys, so delete any backup file
    # which would exist at this point.
    for backup_path in glob.glob(backup_glob): # pragma: no cover
      os.unlink(backup_path)
    before_backup = list(SQLite3Storage(
      self._server_db,
      table_prefix='cau',
    ).dumpIterator())
    self._startServer('--backup-directory', self._server_backup_path)
    backup_path_list = retry(lambda: glob.glob(backup_glob))
    if not backup_path_list: # pragma: no cover
      raise AssertionError('Backup file not created after 1 second')
    backup_path, = backup_path_list
    self._stopServer()

    # Server must refuse to restore if the database still exists
    self.assertNotEqual(
      self._restoreServer(
        backup_path,
        user2_key_path,
        user2_new_csr_path,
        user2_new_key_path,
      ),
      0,
    )

    os.unlink(self._server_db)
    os.unlink(self._server_key)

    with captureStdout() as stdout:
      cli.key_id([
        '--private-key', user_key_path, user2_key_path, user2_new_key_path,
      ])
    key_id_dict = dict(
      line.rsplit(' ', 1)
      for line in stdout.getvalue().splitlines()
    )
    key_id = key_id_dict.pop(user_key_path)
    key2_id = key_id_dict.pop(user2_key_path)
    new_key2_id = key_id_dict.pop(user2_new_key_path)
    self.assertFalse(key_id_dict)
    with captureStdout() as stdout:
      cli.key_id([
        '--backup', backup_path,
      ])
    self.assertItemsEqual(
      [
        backup_path,
        '  ' + key_id,
        '  ' + key2_id,
      ],
      stdout.getvalue().splitlines(),
    )

    try:
      caucase.http.manage(
        argv=(
          '--db', self._server_db,
          '--restore-backup',
          backup_path,
          user2_key_path,
          user2_new_csr_path,
          user2_new_key_path,
        ),
      )
    except SystemExit as e:
      if e.code:
        raise

    after_restore = list(SQLite3Storage(
      self._server_db,
      table_prefix='cau',
    ).dumpIterator())

    CRL_INSERT = b'INSERT INTO "caucrl" '
    CRT_INSERT = b'INSERT INTO "caucrt" '
    REV_INSERT = b'INSERT INTO "caurevoked" '
    def filterBackup(backup, expect_rev):
      """
      Remove all lines which are know to differ between original batabase and
      post-restoration database, so the rest (which must be the majority of the
      database) can be tested to be equal.
      """
      rev_found = not expect_rev
      new_backup = []
      crt_list = []
      for row in backup:
        if row.startswith(CRL_INSERT):
          continue
        if row.startswith(CRT_INSERT):
          crt_list.append(row)
          continue
        if row.startswith(REV_INSERT): # pragma: no cover
          assert not rev_found, 'Unexpected revocation found'
          continue
        new_backup.append(row)
      return new_backup, crt_list

    before_backup, before_crt_list = filterBackup(
      before_backup,
      False,
    )
    after_restore, after_crt_list = filterBackup(
      after_restore,
      True,
    )
    self.assertEqual(
      len(set(after_crt_list).difference(before_crt_list)),
      1,
    )
    self.assertEqual(
      len(set(before_crt_list).difference(after_crt_list)),
      0,
    )
    self.assertItemsEqual(before_backup, after_restore)

    self._startServer('--backup-directory', self._server_backup_path)

    # user2 got a new certificate matching their new key
    utils.getKeyPair(user2_new_key_path)

    # And user 1 must still work without key change
    self._runClient(
      '--user-key', user_key_path,
      '--list-csr',
    )

    # Another backup can happen after restoration
    self._stopServer()
    for backup_path in glob.glob(backup_glob):
      os.unlink(backup_path)
    self._startServer('--backup-directory', self._server_backup_path)
    backup_path_list = retry(lambda: glob.glob(backup_glob))
    if not backup_path_list: # pragma: no cover
      raise AssertionError('Backup file not created after 1 second')
    backup_path, = glob.glob(backup_glob)
    with captureStdout() as stdout:
      cli.key_id([
        '--backup', backup_path,
      ])
    self.assertItemsEqual(
      [
        backup_path,
        '  ' + key_id,
        '  ' + new_key2_id,
      ],
      stdout.getvalue().splitlines(),
    )

    # Now, push a lot of data to exercise chunked checksum in backup &
    # restoration code
    self._stopServer()
    for backup_path in glob.glob(backup_glob):
      os.unlink(backup_path)
    db = sqlite3.connect(self._server_db)
    db.row_factory = sqlite3.Row
    with db:
      c = db.cursor()
      c.execute('CREATE TABLE bloat (bloat TEXT)')
      bloat_query = 'INSERT INTO bloat VALUES (?)'
      bloat_value = ('bloat' * 10240, )
      for _ in xrange(1024):
        c.execute(bloat_query, bloat_value)
    db.close()
    del db
    self._startServer('--backup-directory', self._server_backup_path)
    backup_path_list = retry(lambda: glob.glob(backup_glob), try_count=300)
    if not backup_path_list: # pragma: no cover
      raise AssertionError('Backup file took too long to be created')
    backup_path, = glob.glob(backup_glob)
    with captureStdout() as stdout:
      cli.key_id([
        '--backup', backup_path,
      ])
    self.assertItemsEqual(
      [
        backup_path,
        '  ' + key_id,
        '  ' + new_key2_id,
      ],
      stdout.getvalue().splitlines(),
    )
    self._stopServer()
    os.unlink(self._server_db)
    os.unlink(self._server_key)
    backup_path, = backup_path_list
    # user2 sacrifice their private key, and prepare its replacement
    basename = self._getBaseName()
    user2_newnew_key_path = self._createPrivateKey(basename)
    user2_newnew_csr_path = self._createBasicCSR(
      basename,
      user2_newnew_key_path,
    )
    user2_new_bare_key_path = user2_new_key_path + '.bare_key'
    with open(user2_new_bare_key_path, 'wb') as bare_key_file:
      bare_key_file.write(utils.getKeyPair(user2_new_key_path)[1])
    self.assertEqual(
      self._restoreServer(
        backup_path,
        user2_new_bare_key_path,
        user2_newnew_csr_path,
        user2_newnew_key_path,
      ),
      0,
    )

  def testCAImportExport(self):
    """
    Exercise CA export and import code.
    """
    exported_ca = os.path.join(self._server_dir, 'exported.ca.pem')
    user_key_path = self._createFirstUser()
    # Create a service certificate...
    service_key = self._createAndApproveCertificate(
      user_key_path,
      'service',
    )
    # ...and revoke it
    # Note: Fetches CRL right after revoking certificate
    self._runClient(
      '--revoke-crt', service_key, service_key,
    )
    self._runClient()
    getBytePass_orig = caucase.http.getBytePass
    try:
      caucase.http.getBytePass = lambda x: b'test'
      self.assertFalse(os.path.exists(exported_ca), exported_ca)
      caucase.http.manage(
        argv=(
          '--db', self._server_db,
          '--export-ca', exported_ca,
        ),
      )
      self.assertTrue(os.path.exists(exported_ca), exported_ca)
      server_db2 = self._server_db + '2'
      self.assertFalse(os.path.exists(server_db2), server_db2)
      with captureStdout() as stdout:
        caucase.http.manage(
          argv=(
            '--db', server_db2,
            '--import-ca', exported_ca,
            '--import-crl', self._client_crl,
            # Twice, for code coverage...
            '--import-crl', self._client_crl,
          ),
        )
      self.assertTrue(os.path.exists(server_db2), server_db2)
      self.assertEqual(
        [
          'Imported 1 CA certificates',
          'Revoked 1 certificates (1 were already revoked)',
        ],
        stdout.getvalue().splitlines(),
      )
    finally:
      caucase.http.getBytePass = getBytePass_orig

  def testWSGIBase(self):
    """
    Low-level WSGI tests.

    Not caucase-specific, but testing code which is part of caucase.
    """
    def run(request_line_list, app=DummyApp()):
      """
      Trigger execution of app, with given request.
      """
      wfile = BytesIO()
      caucase.http.CaucaseWSGIRequestHandler(
        FakeStreamRequest(
          BytesIO(b'\r\n'.join(request_line_list + [b''])),
          NoCloseFileProxy(wfile),
        ),
        ('0.0.0.0', 0),
        FakeAppServer(app),
        log_file=self.caucase_test_output,
        error_file=self.caucase_test_output,
      )
      return wfile.getvalue().splitlines()

    def getStatus(response_line_list):
      """
      Naive extraction of http status out of an http response.
      """
      _, code, _ = response_line_list[0].split(b' ', 2)
      return int(code)

    def getBody(response_line_list):
      """
      Naive extraction of http response body.
      """
      return b'\r\n'.join(
        response_line_list[response_line_list.index(b'') + 1:],
      )

    self.assertEqual(
      getStatus(run([b'GET /' + b'a' * 65537])),
      414,
    )
    expect_continue_request = [
      b'PUT / HTTP/1.1',
      b'Expect: 100-continue',
      b'Content-Length: 4',
      b'Content-Type: text/plain',
      b'',
      b'Test',
    ]
    # No read: 200 OK
    self.assertEqual(
      getStatus(run(expect_continue_request)),
      200,
    )
    read_app = DummyApp(lambda environ: [environ['wsgi.input'].read()])
    # Read: 100 Continue (as first response, assume 200 OK happens later)
    self.assertEqual(
      getStatus(run(expect_continue_request, read_app)),
      100,
    )
    # HTTP/1.0: 200 OK
    self.assertEqual(
      getStatus(run(
        [
          b'PUT / HTTP/1.0',
        ] + expect_continue_request[1:],
        read_app,
      )),
      200,
    )

    chunked_request = [
      b'PUT / HTTP/1.1',
      b'Transfer-Encoding: chunked',
      b'',
      b'f;some=extension',
      b'123456789abcd\r\n',
      b'3',
      b'ef0',
      b'0',
      b'X-Chunked-Trailer: blah'
    ]
    self.assertEqual(
      getBody(run(chunked_request, read_app)),
      b'123456789abcd\r\nef0',
    )
    self.assertEqual(
      getBody(run(
        chunked_request,
        DummyApp(lambda environ: [
          environ['wsgi.input'].read(),
          environ['wsgi.input'].read(),
        ]))),
      b'123456789abcd\r\nef0',
    )
    self.assertEqual(
      getBody(run(
        chunked_request,
        DummyApp(lambda environ: [
          environ['wsgi.input'].read(6),
          environ['wsgi.input'].read(),
        ]))),
      b'123456789abcd\r\nef0',
    )
    self.assertEqual(
      getBody(run(
        chunked_request,
        DummyApp(lambda environ: [
          environ['wsgi.input'].read(32),
        ]))),
      b'123456789abcd\r\nef0',
    )

    self.assertEqual(
      getStatus(run([
        b'PUT / HTTP/1.1',
        b'Transfer-Encoding: chunked',
        b'',
        b'1',
        b'abc', # Chunk longer than advertised in header.
      ], read_app)),
      500,
    )
    self.assertEqual(
      getStatus(run([
        b'PUT / HTTP/1.1',
        b'Transfer-Encoding: chunked',
        b'',
        b'y', # Not a valid chunk header
      ], read_app)),
      500,
    )
    self.assertEqual(
      getStatus(run([
        b'PUT / HTTP/1.1',
        b'Transfer-Encoding: chunked',
        b'',
        b'f;' + b'a' * 65537, # header too long
      ], read_app)),
      500,
    )
    self.assertEqual(
      getStatus(run([
        b'PUT / HTTP/1.1',
        b'Transfer-Encoding: chunked',
        b'',
        b'0',
        b'a' * 65537, # trailer too long
      ], read_app)),
      500,
    )

  def testUpdater(self):
    """
    Test updater basic functionality.
    Scenario is:
    - a CSR is generated somewhere, corresponding private key can be discarded
    - CSR is sent to a remote machine, where deployment is happening and
      a service needs a certificate
    - on the machine where deployment happens, a new CSR + private key pair
      is produced, using transmitted CSR as a template, with
      "caucase-rerequest"
    - the new CSR is submitted to caucase using "caucase-updater"
    """
    basename = self._getBaseName()
    key_path = self._createPrivateKey(basename)
    csr_path = self._createBasicCSR(basename, key_path)
    re_key_path = key_path + '2'
    re_csr_path = csr_path + '2'
    re_crt_path = re_csr_path + '.crt'
    self.assertFalse(os.path.exists(re_key_path))
    self.assertFalse(os.path.exists(re_csr_path))
    cli.rerequest(
      argv=(
        '--csr', re_csr_path,
        '--key', re_key_path,
        '--template', csr_path,
      ),
    )
    self.assertTrue(os.path.exists(re_key_path))
    self.assertTrue(os.path.exists(re_csr_path))

    user_key_path = self._createFirstUser()
    self.assertEqual(
      [],
      self._runClient(
        '--user-key', user_key_path,
        '--list-csr',
      ).splitlines()[2:-1],
    )
    self.assertFalse(os.path.exists(re_crt_path))
    updater_event = threading.Event()
    until_updater = UntilEvent(updater_event)
    network_issue_event = threading.Event()
    until_network_issue = UntilEvent(network_issue_event)
    # pylint: disable=protected-access
    cli.RetryingCaucaseClient._until = until_network_issue
    cli.RetryingCaucaseClient._log_file = self.caucase_test_output
    # pylint: enable=protected-access
    until_network_issue.action = ON_EVENT_EXPIRE
    original_HTTPConnection = cli.RetryingCaucaseClient.HTTPConnection
    class ErrorInjector(object):
      """
      Callable instances which set a flag when called and raise provided
      exception.
      """
      reached = False
      def __init__(self, exception):
        self.exception = exception

      def __call__(self, *_, **__):
        self.reached = True
        raise self.exception
    class HTTPConnectionNetworkFaultInjector(original_HTTPConnection):
      """
      Place holder for error injectors (to not poison the real HTTPConnection).
      """
      pass
    def reraise(*_, **__): # pragma: no cover
      """
      Just reraise latest error.
      For replacing RetryingCaucaseClient._until only.
      """
      # pylint: disable=misplaced-bare-raise
      raise
      # pylint: enable=misplaced-bare-raise
    cli.RetryingCaucaseClient.HTTPConnection = HTTPConnectionNetworkFaultInjector
    # Prime the error pump.
    HTTPConnectionNetworkFaultInjector.connect = injector = ErrorInjector(
      socket.gaierror(-3, 'Temporary failure in name resolution'),
    )
    updater_thread = threading.Thread(
      target=cli.updater,
      kwargs={
        'argv': (
          '--ca-url', self._caucase_url,
          '--cas-ca', self._client_ca_crt,
          '--key', re_key_path,
          '--csr', re_csr_path,
          '--crt', re_crt_path,
          '--ca', self._client_ca_crt,
          '--crl', self._client_crl,
        ),
        'until': until_updater,
      },
    )
    updater_thread.daemon = True
    updater_thread.start()
    try:
      # XXX: this error injection technique only tests the first query. Assume
      # the code handle network errors consistently everywhere
      # (IOW, RetryingCaucaseClient is used everywhere).
      for index, (HTTPConnection_method_id, injector) in enumerate((
        ('connect', injector), # Primed above
        ('connect', ErrorInjector(socket.error(111, 'Connection refused'))),
        ('getresponse', ErrorInjector(httplib.BadStatusLine('blah'))),
        ('getresponse', ErrorInjector(httplib.LineTooLong('header line'))),
        ('getresponse', ErrorInjector(httplib.UnknownProtocol('HTTP/pigeon'))),
        ('getresponse', ErrorInjector(httplib.IncompleteRead('you are my '))),
      )):
        if index:
          # Set next fault
          setattr(
            HTTPConnectionNetworkFaultInjector,
            HTTPConnection_method_id,
            injector,
          )
          # Let code reach it
          network_issue_event.set()
        # Wait for the code to reach the fault.
        # XXX: how to fast-fail if thread dies ?
        until_network_issue.wait()
        # Check injector really got triggered.
        self.assertTrue(injector.reached)
        # Cleanup and prepare next error
        delattr(HTTPConnectionNetworkFaultInjector, HTTPConnection_method_id)
      cli.RetryingCaucaseClient.HTTPConnection = original_HTTPConnection
      # pylint: disable=protected-access
      cli.RetryingCaucaseClient._until = reraise
      # pylint: enable=protected-access
      # Let code carry on.
      network_issue_event.set()

      until_updater.wait()
      # CSR must have been submitted
      csr_line_list = self._runClient(
        '--user-key', user_key_path,
        '--list-csr',
      ).splitlines()[2:-1]
      self.assertEqual(1, len(csr_line_list), csr_line_list)
      # Sign it
      self._runClient(
        '--user-key', user_key_path,
        '--sign-csr', csr_line_list[0].split(None, 1)[0],
      )
      # Wake updater
      until_updater.action = ON_EVENT_EXPIRE
      updater_event.set()
      # Wait for it to call "until()" again
      until_updater.wait()
      # It must have retrieved the certificate now.
      self.assertTrue(os.path.exists(re_crt_path))
    finally:
      until_updater.action = ON_EVENT_RAISE
      updater_event.set()
      updater_thread.join(2)

  def testHttpSSLRenewal(self):
    """
    Test that caucased https certificate renewal is functional.
    """
    # http server is started without backups by default, so deadline is ssl
    # renewal deadline. So fake expiration and verify the certificate presented
    # by https server changed.
    parsed_url = urlparse.urlparse(self._caucase_url)
    # Sanity check
    assert parsed_url.scheme == 'http', parsed_url.scheme
    address = (
      parsed_url.hostname,
      443 if parsed_url.port == 80 else parsed_url.port + 1,
    )
    # Wait for server to sleep, and clear.
    self._server_until.wait()
    # Pull certificate.
    before = ssl.get_server_certificate(address)
    # Wake server so it renews certificate.
    self._server_until.action = ON_EVENT_EXPIRE
    self._server_event.set()
    # Wait for it to be back to sleep.
    self._server_until.wait()
    # Verify renewal happened.
    after = ssl.get_server_certificate(address)
    self.assertNotEqual(before, after)

  def _testHttpCustomNetLoc(self, netloc):
    """
    Breaks on OpenSSL < 1.1.0 as it lacks support for validating
    certificates with IP constraints.
    """
    self._skipIfOpenSSLDoesNotSupportIPContraints()
    self._stopServer()
    os.unlink(self._server_key)
    os.unlink(self._server_db)
    port = urlparse.urlparse(self._caucase_url).port
    if port:
      netloc += ':%s' % port
    self._server_netloc = netloc
    self._caucase_url = 'http://' + netloc
    self._startServer()
    user_key_path = self._createFirstUser()
    service_key = self._createAndApproveCertificate(
      user_key_path,
      'service',
    )
    distribution_point, = utils.load_certificate(
      utils.getCert(service_key),
      [
        utils.load_ca_certificate(x)
        for x in utils.getCertList(self._client_ca_crt)
      ],
      None,
    ).extensions.get_extension_for_class(
      x509.CRLDistributionPoints,
    ).value
    uri, = distribution_point.full_name
    self.assertEqual(uri.value, self._caucase_url + u'/cas/crl')

  def testHttpNetlocIPv4(self):
    """
    Test that it is possible to use a literal IPv4 as netloc.
    """
    self._testHttpCustomNetLoc(netloc='127.0.0.1')

  def testHttpNetlocIPv6(self):
    """
    Test that it is possible to use a literal IPv6 as netloc.
    This used to fail because cryptography module would reject bare IPv6
    address in CRL distribution point extension (unlike IPv4).
    """
    self._testHttpCustomNetLoc(netloc='[::1]')

  def testServerFilePermissions(self):
    """
    Check that both the sqlite database and server keys are group- and
    other-inaccessible (u=rw,go=).
    Only check "regular" permissions (3 octal least significant digits).
    Limitation: Does not try to race against server.
    """
    self.assertEqual(os.stat(self._server_db).st_mode & 0o777, 0o600)
    self.assertEqual(os.stat(self._server_key).st_mode & 0o777, 0o600)

for property_id, property_value in CaucaseTest.__dict__.iteritems():
  if property_id.startswith('test') and callable(property_value):
    setattr(CaucaseTest, property_id, print_buffer_on_error(property_value))

# pylint: disable=no-member
if getattr(CaucaseTest, 'assertItemsEqual', None) is None: # pragma: no cover
  # Because python3 decided it should be named differently, and 2to3 cannot
  # pick it up, and this code must remain python2-compatible... Yay !
  CaucaseTest.assertItemsEqual = CaucaseTest.assertCountEqual
# pylint: enable=no-member

if __name__ == '__main__': # pragma: no cover
  unittest.main()

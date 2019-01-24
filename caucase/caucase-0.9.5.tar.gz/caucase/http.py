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
from __future__ import absolute_import, print_function
import argparse
from collections import defaultdict
import datetime
import errno
from functools import partial
from getpass import getpass
import glob
import itertools
import json
import os
import socket
from SocketServer import ThreadingMixIn
import ssl
import sys
import tempfile
from threading import Thread
from urlparse import urlparse, urlunsplit
from wsgiref.simple_server import make_server, WSGIServer
import ipaddress
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import pem
from . import exceptions
from . import utils
from . import version
from .wsgi import Application, CORSTokenManager
from .ca import CertificateAuthority, UserCertificateAuthority, Extension
from .storage import SQLite3Storage
from .http_wsgirequesthandler import WSGIRequestHandler

_cryptography_backend = default_backend()

BACKUP_SUFFIX = '.sql.caucased'

def getBytePass(prompt): # pragma: no cover
  """
  Like getpass, but resurns a bytes instance.
  """
  result = getpass(prompt)
  if not isinstance(result, bytes):
    result = result.encode(sys.stdin.encoding)
  return result

def _createKey(path):
  """
  Open a key file, setting it to minimum permission if it gets created.
  Does not change umask, to be thread-safe.

  Returns a python file object, opened for write-only.
  """
  return os.fdopen(
    os.open(path, os.O_WRONLY | os.O_CREAT, 0o600),
    'wb',
  )

class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
  """
  Threading WSGI server
  """
  daemon_threads = True

  def __init__(self, server_address, *args, **kw):
    self._error_file = kw.pop('error_file', sys.stderr)
    self.address_family, _, _, _, _ = socket.getaddrinfo(*server_address)[0]
    WSGIServer.__init__(
      self,
      server_address,
      bind_and_activate=False,
      *args,
      **kw
    )

  def server_bind(self):
    if self.address_family == socket.AF_INET6:
      # Separate IPv6 and IPv4 port spaces
      self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
    WSGIServer.server_bind(self)

  def handle_error(self, request, client_address):
    """
    Handle an error gracefully.
    """
    utils.log_exception(
      error_file=self._error_file,
      exc_info=sys.exc_info(),
      client_address=client_address[0],
    )

  # pylint: disable=arguments-differ
  def serve_forever(self, *args, **kw):
    """
    Handle one request at a time until shutdown.

    In addition to python's version:
    - intercept EBADF on shutdown if select is interrupted:
    """
    try:
      return WSGIServer.serve_forever(self, *args, **kw)
    except socket.error as exception: # pragma: no cover
      # Workaround for the following unhandled error:
      # Traceback (most recent call last):
      #   File "/usr/lib/python2.7/threading.py", line 801, in __bootstrap_inner
      #     self.run()
      #   File "/usr/lib/python2.7/threading.py", line 754, in run
      #     self.__target(*self.__args, **self.__kwargs)
      #   File "/usr/lib/python2.7/SocketServer.py", line 231, in serve_forever
      #     poll_interval)
      #   File "/usr/lib/python2.7/SocketServer.py", line 150, in _eintr_retry
      #     return func(*args)
      #   File "/usr/lib/python2.7/SocketServer.py", line 459, in fileno
      #     return self.socket.fileno()
      #   File "/usr/lib/python2.7/socket.py", line 228, in meth
      #     return getattr(self._sock,name)(*args)
      #   File "/usr/lib/python2.7/socket.py", line 174, in _dummy
      #     raise error(EBADF, 'Bad file descriptor')
      # error: [Errno 9] Bad file descriptor
      # Sadly, self.__shutdown_request is not accessible from here, so do not
      # check any further.
      if exception.errno != errno.EBADF:
        raise
  # pylint: enable=arguments-differ

def _buildQuoteCharList():
  # All chars considered guilty
  result = ['\\x%02x' % x for x in xrange(256)]
  # Exception for non-printable whitespaces.
  result[ord('\b')] = '\\b'
  result[ord('\n')] = '\\n'
  result[ord('\r')] = '\\r'
  result[ord('\t')] = '\\t'
  result[ord('\v')] = '\\v'
  # Exception for printable chars
  for x in xrange(0x20, 0x7f):
    result[x] = chr(x)
  # Exception in the exception: chars which need escapement
  result[ord('\\')] = '\\\\'
  result[ord('"')] = '\\"'
  return result
_QUOTE_LOG_LIST = _buildQuoteCharList()
del _buildQuoteCharList

class CaucaseWSGIRequestHandler(WSGIRequestHandler):
  """
  Make WSGIRequestHandler logging more apache-like and allow choosing a file
  other than stderr for log output.
  """
  server_version = 'caucased ' + version.__version__
  remote_user_name = '-'

  def __init__(self, *args, **kw):
    self._log_file = kw.pop('log_file', sys.stdout)
    self._error_file = kw.pop('error_file', sys.stderr)
    WSGIRequestHandler.__init__(self, *args, **kw)

  def log_date_time_string(self):
    """
    Apache-style date format.

    Compared to python's default (from BaseHTTPServer):
    - ":" between day and time
    - "+NNNN" timezone is displayed
    - ...but, because of how impractical it is in python to get system current
      timezone (including DST considerations), time it always logged in GMT
    """
    now = datetime.datetime.utcnow()
    return now.strftime(
      '%d/' + self.monthname[now.month] + '/%Y:%H:%M:%S +0000',
    )

  def log_request(self, code='-', size='-'):
    """
    Log request. Happens after response was sent.

    Compared to python's default (from BaseHTTPServer):
    - log referrer
    - log user agent
    - escaping
    """
    headers = getattr(self, 'headers', {})
    self.log_message(
      '"%s" %s %s "%s" "%s"',
      ''.join(_QUOTE_LOG_LIST[ord(x)] for x in self.requestline),
      code,
      size,
      ''.join(_QUOTE_LOG_LIST[ord(x)] for x in headers.get('Referrer', '-')),
      ''.join(_QUOTE_LOG_LIST[ord(x)] for x in headers.get('User-Agent', '-')),
    )

  # pylint: disable=redefined-builtin
  def log_message(self, format, *args):
    """
    Log an arbitrary message.

    Compared to python's default (from BaseHTTPServer):
    - make remote user name customisable (used in CaucaseSSLWSGIRequestHandler)
    - make output stream customisable
    - use print instead of plain .write(), for encoding purposes
    """
    print(
      '%s - %s [%s] %s' % (
        self.client_address[0],
        self.remote_user_name,
        self.log_date_time_string(),
        format % args,
      ),
      file=self._log_file,
    )
  # pylint: enable=redefined-builtin

  def get_stderr(self):
    """
    Send wsgi.errors to error output.
    """
    return self._error_file

class CaucaseSSLWSGIRequestHandler(CaucaseWSGIRequestHandler):
  """
  Add SSL-specific entries to environ:
  - HTTPS=on
  - SSL_CLIENT_CERT when client has sent a certificate.
  - use certificate serial as user name
  """
  def get_environ(self):
    """
    Populate environment.
    """
    environ = CaucaseWSGIRequestHandler.get_environ(self)
    environ['HTTPS'] = 'on'
    client_cert_der = self.request.getpeercert(binary_form=True)
    if client_cert_der is not None:
      cert = x509.load_der_x509_certificate(
        client_cert_der,
        _cryptography_backend,
      )
      self.remote_user_name = str(cert.serial_number)
      environ['SSL_CLIENT_CERT'] = utils.dump_certificate(cert)
    return environ

def startServerThread(server):
  """
  Create and start a "serve_forever" thread.
  """
  server_thread = Thread(target=server.serve_forever)
  server_thread.daemon = True
  server_thread.start()

def getSSLContext(
  key_len,
  threshold,
  server_key_path,
  hostname_ip_address,
  hostname_dnsname,
  cau,
  http_cas,
  renew=False, # Force renewal when True - used in tests
):
  """
  Build a new SSLContext with updated CA certificates, CRL and server key pair,
  and return it along with the datetime of next update.
  """
  ssl_context = ssl.create_default_context(
    purpose=ssl.Purpose.CLIENT_AUTH,
  )
  # SSL is used for client authentication, and is only required for very few
  # users on any given caucased. So make ssl_context even stricter than python
  # does.
  # No TLSv1 and TLSv1.1, leaving (currently) only TLSv1.2
  ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

  # If a client wishes to use https for unauthenticated operations, that's
  # fine too.
  ssl_context.verify_mode = ssl.CERT_OPTIONAL
  # Note: python's standard ssl module does not provide a way to replace the
  # current CRL file on an existing openssl context: load_verify_locations ends
  # up calling X509_STORE_add_crl, which either adds the CRL to its list of
  # files or rejects the file. So either memory usage with increase until
  # context gets renewed, or we get stuck with an old CRL. So expect wsgi
  # application to implement these checks on its own when accessing client's
  # certificate.
  #ssl_context.verify_flags = ssl.VERIFY_CRL_CHECK_LEAF
  ssl_context.load_verify_locations(
    cadata=utils.toUnicode(cau.getCACertificate()),
  )
  http_cas_certificate_list = http_cas.getCACertificateList()
  threshold_delta = datetime.timedelta(threshold, 0)
  exists = os.path.exists(server_key_path)
  if exists:
    try:
      old_crt_pem = utils.getLeafCertificate(server_key_path)
      old_crt = utils.load_certificate(
        old_crt_pem,
        http_cas_certificate_list,
        None,
      )
    except Exception: # pylint: disable=broad-except
      exists = False
  if exists:
    if renew or (
      old_crt.not_valid_after - threshold_delta < datetime.datetime.utcnow()
    ):
      new_key = utils.generatePrivateKey(key_len)
      new_key_pem = utils.dump_privatekey(new_key)
      new_crt_pem = http_cas.renew(
        crt_pem=old_crt_pem,
        csr_pem=utils.dump_certificate_request(
          x509.CertificateSigningRequestBuilder(
          ).subject_name(
            # Note: caucase server ignores this, but cryptography
            # requires CSRs to have a subject.
            old_crt.subject,
          ).sign(
            private_key=new_key,
            algorithm=utils.DEFAULT_DIGEST_CLASS(),
            backend=_cryptography_backend,
          ),
        ),
      )
      new_ca_crt_pem = http_cas.getCACertificate()
      with _createKey(server_key_path) as crt_file:
        crt_file.write(new_key_pem)
        crt_file.write(new_crt_pem)
        crt_file.write(new_ca_crt_pem)
  else:
    new_key = utils.generatePrivateKey(key_len)
    csr_id = http_cas.appendCertificateSigningRequest(
      csr_pem=utils.dump_certificate_request(
        x509.CertificateSigningRequestBuilder(
          subject_name=x509.Name([
            x509.NameAttribute(
              oid=x509.oid.NameOID.ORGANIZATIONAL_UNIT_NAME,
              value=hostname_dnsname,
            ),
          ]),
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
            Extension(
              x509.SubjectAlternativeName([
                x509.DNSName(hostname_dnsname)
                if hostname_ip_address is None else
                x509.IPAddress(hostname_ip_address)
              ]),
              critical=True,
            ),
          ],
        ).sign(
          private_key=new_key,
          algorithm=utils.DEFAULT_DIGEST_CLASS(),
          backend=_cryptography_backend,
        ),
      ),
      override_limits=True,
    )
    http_cas.createCertificate(csr_id)
    new_crt_pem = http_cas.getCertificate(csr_id)
    new_key_pem = utils.dump_privatekey(new_key)
    new_ca_crt_pem = http_cas.getCACertificate()
    with _createKey(server_key_path) as crt_file:
      crt_file.write(new_key_pem)
      crt_file.write(new_crt_pem)
      crt_file.write(new_ca_crt_pem)
  ssl_context.load_cert_chain(server_key_path)
  return (
    ssl_context,
    utils.load_certificate(
      utils.getLeafCertificate(server_key_path),
      http_cas_certificate_list,
      None,
    ).not_valid_after - threshold_delta,
  )

def main(
  argv=None,
  until=utils.until,
  log_file=sys.stdout,
  error_file=sys.stderr,
):
  """
  Caucase stand-alone http server.
  """
  parser = argparse.ArgumentParser(
    description='caucased',
  )
  parser.add_argument(
    '--version',
    action='version',
    version=version.__version__,
  )
  parser.add_argument(
    '--db',
    default='caucase.sqlite',
    help='Path to the SQLite database. default: %(default)s',
  )
  parser.add_argument(
    '--server-key',
    default='server.key.pem',
    metavar='KEY_PATH',
    help='Path to the ssl key pair to use for https socket. '
    'default: %(default)s',
  )
  parser.add_argument(
    '--cors-key-store',
    default='cors.key',
    metavar='PATH',
    help='Path to a file containing CORS token keys. default: %(default)s',
  )
  parser.add_argument(
    '--cors-whitelist',
    default=[],
    nargs='+',
    metavar='URL',
    help='Origin values to always trust. default: none',
  )
  parser.add_argument(
    '--netloc',
    required=True,
    help='<host>[:<port>] at which certificate verificators may reach this '
    'service. This value is embedded in generated certificates (as CRL '
    'distribution point, as CA certificate common name, possibly more). '
    'See --base-port for how https port is derived from this port. '
    'Note on encoding: only ascii is currently supported. Non-ascii may be '
    'provided idna-encoded.',
  )
  parser.add_argument(
    '--base-port',
    type=int,
    help='Port at which caucase locally binds to provide HTTP service. '
    'If this port is 80, HTTPS service is provided on port 443, otherwise '
    'it is provided on --base-port + 1. '
    'If derived HTTPS port is not available, caucase will exit with an error '
    'status. default: --netloc\'s port, or 80',
  )
  parser.add_argument(
    '--bind',
    default=[],
    action='append',
    help='Address on which caucase locally binds. '
    'default: addresses --netloc\'s <host> resolves into.',
  )
  parser.add_argument(
    '--threshold',
    default=31,
    type=float,
    help='The remaining certificate validity period, in days, under '
    'which a renew is desired. default: %(default)s',
  )
  parser.add_argument(
    '--key-len',
    default=2048,
    type=int,
    metavar='BITLENGTH',
    help='Number of bits to use when generating a new private key. '
    'default: %(default)s',
  )

  service_group = parser.add_argument_group(
    'CAS options: normal certificates, which are not given any privilege on '
    'caucased',
  )

  user_group = parser.add_argument_group(
    'CAU options: special certificates, which are allowed to sign other '
    'certificates and can decrypt backups',
  )

  service_group.add_argument(
    '--service-crt-validity',
    default=3 * 31,
    type=float,
    metavar='DAYS',
    help='Number of days an issued certificate is valid for. '
    'default: %(default)s',
  )
  user_group.add_argument(
    '--user-crt-validity',
    default=3 * 31,
    type=float,
    metavar='DAYS',
    help='Number of days an issued certificate is valid for. '
    'default: %(default)s',
  )

  service_group.add_argument(
    '--service-max-csr',
    default=50,
    type=int,
    help='Maximum number of pending CSR. Further CSR get refused until '
    'an existing ones gets signed or rejected. default: %(default)s',
  )
  user_group.add_argument(
    '--user-max-csr',
    default=50,
    type=int,
    help='Maximum number of pending CSR. Further CSR get refused until '
    'an existing ones gets signed or rejected. default: %(default)s',
  )

  service_group.add_argument(
    '--service-auto-approve-count',
    default=0,
    type=int,
    metavar='COUNT',
    help='Number service certificates which should be automatically signed on '
    'submission, excluding the one needed to serve caucase. '
    'default: %(default)s',
  )
  user_group.add_argument(
    '--user-auto-approve-count',
    default=1,
    type=int,
    metavar='COUNT',
    help='Number of user certificates which should be automatically signed on '
    'submission. default: %(default)s',
  )

  parser.add_argument(
    '--lock-auto-approve-count',
    action='store_true',
    help='The first time this option is given, --service-auto-approve-count '
    'and --user-auto-approve-count values are stored inside caucase database '
    'and will not be altered by further invocations. Once the respective '
    'certificate issuance counters reach these values, no further '
    'certificates will be ever automatically signed.',
  )

  backup_group = parser.add_argument_group(
    'Backup options',
  )
  backup_group.add_argument(
    '--backup-directory',
    help='Backup directory path. Backups will be periodically stored in '
    'given directory, encrypted with all user certificates which are valid '
    'at backup generation time. Any one of the associated private keys can '
    'decypher it. If not set or no user certificate exists, no backup will '
    'be created.',
  )
  backup_group.add_argument(
    '--backup-period',
    default=1,
    type=float,
    help='Number of days between backups. default: %(default)s',
  )
  args = parser.parse_args(argv)

  base_url = u'http://' + utils.toUnicode(args.netloc)
  parsed_base_url = urlparse(base_url)
  hostname = parsed_base_url.hostname
  name_constraints_permited = []
  name_constraints_excluded = []
  hostname_dnsname = utils.toUnicode(hostname)
  try:
    hostname_ip_address = ipaddress.ip_address(hostname_dnsname)
  except ValueError:
    # Hostname is not an ip address, it must be a hostname
    name_constraints_permited.append(
      x509.DNSName(hostname_dnsname),
    )
    hostname_ip_address = None
  else:
    # Hostname is an ip address, forbid hostname claims.
    name_constraints_excluded.append(
      x509.DNSName(u''),
    )
    # Convert to a network to meet NameConstraint restrictions.
    # Resulting network has maximal prefix length, so it really just covers
    # one IP.
    name_constraints_permited.append(
      x509.IPAddress(ipaddress.ip_network(hostname_ip_address)),
    )

  http_port = (
    parsed_base_url.port
    if args.base_port is None
    else args.base_port
  )
  https_port = 443 if http_port == 80 else http_port + 1
  cau_crt_life_time = args.user_crt_validity
  # Certificate Authority for Users: emitted certificate are trusted by this
  # service.
  cau = UserCertificateAuthority(
    storage=SQLite3Storage(
      db_path=args.db,
      table_prefix='cau',
      max_csr_amount=args.user_max_csr,
      # Effectively disables certificate pruning
      crt_keep_time=cau_crt_life_time,
      crt_read_keep_time=cau_crt_life_time,
      enforce_unique_key_id=True,
    ),
    ca_subject_dict={
      'CN': u'Caucase CAU' + (
        u'' if base_url is None else u' at ' + base_url + '/cau'
      ),
    },
    ca_key_size=args.key_len,
    crt_life_time=cau_crt_life_time,
    auto_sign_csr_amount=args.user_auto_approve_count,
    lock_auto_sign_csr_amount=args.lock_auto_approve_count,
  )
  # Certificate Authority for Services: server and client certificates, the
  # final produce of caucase.
  cas = CertificateAuthority(
    storage=SQLite3Storage(
      db_path=args.db,
      table_prefix='cas',
      max_csr_amount=args.service_max_csr,
    ),
    ca_subject_dict={
      'CN': u'Caucase CAS' + (
        u'' if base_url is None else u' at ' + base_url + '/cas'
      ),
    },
    crl_base_url=None if base_url is None else base_url + u'/cas/crl',
    ca_key_size=args.key_len,
    crt_life_time=args.service_crt_validity,
    auto_sign_csr_amount=args.service_auto_approve_count,
    lock_auto_sign_csr_amount=args.lock_auto_approve_count,
  )
  # Certificate Authority for caucased https service. Distinct from CAS to be
  # able to restrict the validity scope of produced CA certificate, so that it
  # can be trusted by genral-purpose https clients without introducing the risk
  # of producing rogue certificates.
  # This Certificate Authority is only internal to this service, and not exposed
  # to http(s), as it can and must only be used to caucased https certificate
  # signature. Only the CA certificate is exposed, to allow verification.
  https_base_url = urlunsplit((
    'https',
    '[' + hostname + ']:' + str(https_port),
    '/',
    None,
    None,
  ))
  http_cas = CertificateAuthority(
    storage=SQLite3Storage(
      db_path=args.db,
      table_prefix='http_cas',
    ),
    ca_subject_dict={
      'CN': u'Caucased CA at ' + https_base_url,
    },
    ca_extension_list=[
      Extension(
        x509.NameConstraints(
          permitted_subtrees=name_constraints_permited,
          excluded_subtrees=name_constraints_excluded or None,
        ),
        critical=True,
      ),
    ],
    ca_key_size=args.key_len,
    # This CA certificate will be installed in browser key stores, where
    # automated renewal will be unlikely to happen. As this CA certificate
    # will only sign caucased https certificates for this process, assume
    # very little will leak from the private key with each signed certificate.
    # So it should be safe and more practical to give it a long life.
    ca_life_period=40, # approx. 10 years
    crt_life_time=args.service_crt_validity,
  )
  if os.path.exists(args.cors_key_store):
    with open(args.cors_key_store, 'rb') as cors_key_file:
      cors_secret_list = json.load(cors_key_file)
  else:
    cors_secret_list = []
  def saveCORSKeyList(cors_secret_list):
    """
    Update CORS key store when a new key was generated.
    """
    with _createKey(args.cors_key_store) as cors_key_file:
      json.dump(cors_secret_list, cors_key_file)
  application = Application(
    cau=cau,
    cas=cas,
    http_url=urlunsplit((
      'http',
      '[' + hostname + ']:' + str(http_port),
      '/',
      None,
      None,
    )),
    https_url=https_base_url,
    cors_token_manager=CORSTokenManager(
      secret_list=cors_secret_list,
      onNewKey=saveCORSKeyList,
    ),
    cors_whitelist=args.cors_whitelist,
  )
  http_list = []
  https_list = []
  known_host_set = set()
  for bind in args.bind or [hostname]:
    for family, _, _, _, sockaddr in socket.getaddrinfo(
      bind,
      0,
      socket.AF_UNSPEC,
      socket.SOCK_STREAM,
      socket.IPPROTO_TCP,
    ):
      if family == socket.AF_INET:
        host, _ = sockaddr
      elif family == socket.AF_INET6:
        host, _, _, _ = sockaddr
      else:
        continue
      if host in known_host_set:
        continue
      known_host_set.add(host)
      print(
        'Listening on [%s]:%i-%i' % (
          host,
          http_port,
          https_port,
        ),
        file=error_file,
      )
      http_list.append(
        make_server(
          host=host,
          port=http_port,
          app=application,
          server_class=partial(
            ThreadingWSGIServer,
            error_file=error_file,
          ),
          handler_class=partial(
            CaucaseWSGIRequestHandler,
            log_file=log_file,
            error_file=error_file,
          ),
        ),
      )
      https_list.append(
        make_server(
          host=host,
          port=https_port,
          app=application,
          server_class=partial(
            ThreadingWSGIServer,
            error_file=error_file,
          ),
          handler_class=partial(
            CaucaseSSLWSGIRequestHandler,
            log_file=log_file,
            error_file=error_file,
          ),
        ),
      )
  ssl_context, next_ssl_update = getSSLContext(
    key_len=args.key_len,
    threshold=args.threshold,
    server_key_path=args.server_key,
    hostname_ip_address=hostname_ip_address,
    hostname_dnsname=hostname_dnsname,
    cau=cau,
    http_cas=http_cas,
  )
  next_deadline = next_ssl_update
  for https in https_list:
    https.socket = ssl_context.wrap_socket(
      sock=https.socket,
      server_side=True,
    )
  if args.backup_directory:
    backup_period = datetime.timedelta(args.backup_period, 0)
    try:
      next_backup = max(
        datetime.datetime.utcfromtimestamp(os.stat(x).st_ctime)
        for x in glob.iglob(
          os.path.join(args.backup_directory, '*' + BACKUP_SUFFIX),
        )
      ) + backup_period
    except ValueError:
      next_backup = datetime.datetime.utcnow()
    next_deadline = min(
      next_deadline,
      next_backup,
    )
  else:
    next_backup = None
  for server in itertools.chain(http_list, https_list):
    try:
      server.server_bind()
      server.server_activate()
    except:
      server.server_close()
      raise
    startServerThread(server)
  try:
    while True:
      now = until(next_deadline)
      if now >= next_ssl_update:
        ssl_context, next_ssl_update = getSSLContext(
          key_len=args.key_len,
          threshold=args.threshold,
          server_key_path=args.server_key,
          hostname_ip_address=hostname_ip_address,
          hostname_dnsname=hostname_dnsname,
          cau=cau,
          http_cas=http_cas,
          renew=True,
        )
        for https in https_list:
          ssl_socket = https.socket
          try:
            ssl_socket.context = ssl_context
          except AttributeError:
            # Workaround for python bug 34747: changing a listening
            # SSLSocket's SSL context fails on
            # "self._sslobj.context = context" while "self._sslobj" is only
            # set on connected sockets.
            # Luckily is it done just after updating "self._context" which is
            # what is actually used when accepting a connection - so the update
            # is actually successful.
            pass
      if next_backup is None:
        next_deadline = next_ssl_update
      else:
        if now >= next_backup:
          tmp_backup_fd, tmp_backup_path = tempfile.mkstemp(
            prefix='caucase_backup_',
          )
          with os.fdopen(tmp_backup_fd, 'wb') as backup_file:
            result = cau.doBackup(backup_file.write)
          if result:
            backup_path = os.path.join(
              args.backup_directory,
              now.strftime('%Y%m%d%H%M%S') + BACKUP_SUFFIX,
            )
            os.rename(tmp_backup_path, backup_path)
            next_backup = now + backup_period
          else:
            os.unlink(tmp_backup_path)
            next_backup = now + datetime.timedelta(0, 3600)
        next_deadline = min(
          next_ssl_update,
          next_backup,
        )
  except utils.SleepInterrupt:
    pass
  finally:
    print('Exiting', file=error_file)
    for server in itertools.chain(http_list, https_list):
      server.server_close()
      server.shutdown()

def manage(argv=None):
  """
  caucased database management tool.
  """
  parser = argparse.ArgumentParser(
    description='caucased caucased database management tool',
  )
  parser.add_argument(
    '--version',
    action='version',
    version=version.__version__,
  )
  parser.add_argument(
    '--db',
    default='caucase.sqlite',
    help='Path to the SQLite database. default: %(default)s',
  )
  parser.add_argument(
    '--user-crt-validity',
    default=3 * 31,
    type=float,
    metavar='DAYS',
    help='Number of days an issued certificate is valid for. Useful with '
    '--restore-backup as a new user certificate must be produced. '
    'default: %(default)s',
  )

  parser.add_argument(
    '--restore-backup',
    nargs=4,
    metavar=('BACKUP_PATH', 'KEY_PATH', 'CSR_PATH', 'CRT_PATH'),
    help='Restore the file at BACKUP_PATH, decyphering it with the key '
    'at KEY_PATH, revoking corresponding certificate and issuing a new '
    'one in CRT_PATH using the public key in CSR_PATH. '
    'Fails if database exists.',
  )
  parser.add_argument(
    '--import-ca',
    default=[],
    metavar='PEM_FILE',
    action='append',
    type=argparse.FileType('rb'),
    help='Import key pairs as initial service CA certificate. '
    'May be provided multiple times to import multiple key pairs. '
    'Keys and certificates may be in separate files. '
    'If there are multiple keys or certificates, all will be imported. '
    'Will fail if there is any certificate without a key, or vice-versa, '
    'or if any certificate is not suitable for use as a CA certificate. '
    'Caucase-initiated CA renewal, which will happen when latest provided '
    'has less than 3 times --service-crt-validity validity period left, '
    'will copy that CA\'s extensions to produce the new certificate. '
    'Passphrase will be prompted for each protected key.',
  )
  parser.add_argument(
    '--import-bad-ca',
    action='store_true',
    default=False,
    help='Do not check sanity of imported CA certificates. Useful when '
    'migrating a custom CA where clients do very customised checks. Do not '
    'use this unless you are certain you need it and it is safe for your '
    'use-case.',
  )
  parser.add_argument(
    '--import-crl',
    default=[],
    metavar='PEM_FILE',
    action='append',
    type=argparse.FileType('rb'),
    help='Import service revocation list. Corresponding CA certificate must '
    'be already present in the database (including added in the same run '
    'using --import-ca).',
  )
  parser.add_argument(
    '--export-ca',
    metavar='PEM_FILE',
    type=argparse.FileType('wb'),
    help='Export all CA certificates in a PEM file. Passphrase will be '
    'prompted to protect all keys.',
  )
  args = parser.parse_args(argv)
  db_path = args.db
  if args.restore_backup:
    (
      backup_path,
      backup_key_path,
      backup_csr_path,
      backup_crt_path,
    ) = args.restore_backup
    try:
      _, key_pem, _ = utils.getKeyPair(backup_key_path)
    except ValueError:
      # maybe user extracted their private key ?
      key_pem = utils.getKey(backup_key_path)
    cau_crt_life_time = args.user_crt_validity
    with open(
      backup_path,
      'rb',
    ) as backup_file, open(
      backup_crt_path,
      'ab',
    ) as new_crt_file:
      new_crt_file.write(
        UserCertificateAuthority.restoreBackup(
          db_class=SQLite3Storage,
          db_path=db_path,
          read=backup_file.read,
          key_pem=key_pem,
          csr_pem=utils.getCertRequest(backup_csr_path),
          db_kw={
            'table_prefix': 'cau',
            # max_csr_amount: not needed, renewal ignores quota
            # Effectively disables certificate expiration
            'crt_keep_time': cau_crt_life_time,
            'crt_read_keep_time': cau_crt_life_time,
            'enforce_unique_key_id': True,
          },
          kw={
            # Disable CA cert renewal
            'ca_key_size': None,
            'crt_life_time': cau_crt_life_time,
          },
        ),
      )
  if args.import_ca:
    import_ca_dict = defaultdict(
      (lambda: {'crt': None, 'key': None, 'from': []}),
    )
    for ca_file in args.import_ca:
      for index, component in enumerate(pem.parse(ca_file.read())):
        name = '%r, block %i' % (ca_file.name, index)
        if isinstance(component, pem.Certificate):
          component_name = 'crt'
          component_value = x509.load_pem_x509_certificate(
            component.as_bytes(),
            _cryptography_backend,
          )
        elif isinstance(component, pem.Key):
          password = None
          while True:
            component_name = 'key'
            try:
              component_value = serialization.load_pem_private_key(
                component.as_bytes(),
                password,
                _cryptography_backend,
              )
            except TypeError:
              password = getBytePass('Passphrase for key at %s: ' % (name, ))
            else:
              break
        else:
          raise TypeError('%s is of unsupported type %r' % (
            name,
            type(component),
          ))
        import_ca = import_ca_dict[
          x509.SubjectKeyIdentifier.from_public_key(
            component_value.public_key(),
          ).digest
        ]
        import_ca[component_name] = component_value
        import_ca['from'].append(name)
    now = utils.datetime2timestamp(datetime.datetime.utcnow())
    imported = 0
    cas_db = SQLite3Storage(
      db_path,
      table_prefix='cas',
    )
    for identifier, ca_pair in import_ca_dict.iteritems():
      found_from = ', '.join(ca_pair['from'])
      crt = ca_pair['crt']
      if crt is None:
        print(b'No certificate correspond to', found_from, b'- skipping')
        continue
      expiration = utils.datetime2timestamp(crt.not_valid_after)
      if expiration < now:
        print(b'Skipping expired certificate from', found_from)
        del import_ca_dict[identifier]
        continue
      if not args.import_bad_ca:
        try:
          basic_contraints = crt.extensions.get_extension_for_class(
            x509.BasicConstraints,
          )
          key_usage = crt.extensions.get_extension_for_class(
            x509.KeyUsage,
          ).value
        except x509.ExtensionNotFound:
          failed = True
        else:
          failed = (
            not basic_contraints.value.ca or not basic_contraints.critical
            or not key_usage.key_cert_sign or not key_usage.crl_sign
          )
        if failed:
          print(b'Skipping non-CA certificate from', found_from)
          continue
      key = ca_pair['key']
      if key is None:
        print(b'No private key correspond to', found_from, b'- skipping')
        continue
      imported += 1
      cas_db.appendCAKeyPair(
        expiration,
        {
          'key_pem': utils.dump_privatekey(key),
          'crt_pem': utils.dump_certificate(crt),
        },
      )
    if not imported:
      raise ValueError('No CA certificate imported')
    print(b'Imported %i CA certificates' % imported)
  if args.import_crl:
    db = SQLite3Storage(db_path, table_prefix='cas')
    trusted_ca_crt_set = [
      utils.load_ca_certificate(x['crt_pem'])
      for x in db.getCAKeyPairList()
    ]
    latest_ca_not_after = max(
      x.not_valid_after
      for x in trusted_ca_crt_set
    )
    already_revoked_count = revoked_count = 0
    for crl_file in args.import_crl:
      for revoked in utils.load_crl(crl_file.read(), trusted_ca_crt_set):
        try:
          db.revoke(
            revoked.serial_number,
            latest_ca_not_after,
          )
        except exceptions.Found:
          already_revoked_count += 1
        else:
          revoked_count += 1
    print(b'Revoked %i certificates (%i were already revoked)' % (
      revoked_count,
      already_revoked_count,
    ))
  if args.export_ca is not None:
    encryption_algorithm = serialization.BestAvailableEncryption(
      getBytePass('CA export passphrase: ')
    )
    write = args.export_ca.write
    for key_pair in SQLite3Storage(
      db_path,
      table_prefix='cas',
    ).getCAKeyPairList():
      write(
        key_pair['crt_pem'] + serialization.load_pem_private_key(
          key_pair['key_pem'],
          None,
          _cryptography_backend,
        ).private_bytes(
          encoding=serialization.Encoding.PEM,
          format=serialization.PrivateFormat.TraditionalOpenSSL,
          encryption_algorithm=encryption_algorithm,
        ),
      )
    args.export_ca.close()

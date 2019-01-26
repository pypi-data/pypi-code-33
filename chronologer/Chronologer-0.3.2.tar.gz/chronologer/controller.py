import sys
import json
import hashlib
import logging
import itertools
from hmac import compare_digest
from http import HTTPStatus
from collections import namedtuple
from datetime import datetime, timezone, timedelta

import rules
import schedule
import cherrypy.lib
from cherrypy.process.plugins import Monitor

from .storage import StorageQueryError, StorageError
from .model import createRecord, groupTimeseries, ModelError


__all__ = 'RecordApi', 'authenticate'

logger = logging.getLogger(__name__)


def jsonoutTool(fn):
  '''Wrapper around built-in tool to pass ``default = str`` to encoder.'''

  def json_encode(value):
    for chunk in json.JSONEncoder(default = str).iterencode(value):
      yield chunk.encode()

  def json_handler(*args, **kwargs):
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)  # @UndefinedVariable
    return json_encode(value)

  return cherrypy.tools.json_out(handler = json_handler)(fn)  # @UndefinedVariable

cherrypy.tools.jsonout = jsonoutTool
cherrypy.tools.jsonin  = cherrypy.tools.json_in  # @UndefinedVariable


def ndjsonGenerator(fp):
  lineno = 0
  try:
    while True:
      line = fp.readline().decode()
      if not line:
        break
      lineno += 1
      yield json.loads(line)
  except (json.JSONDecodeError, UnicodeDecodeError):
    raise ValueError('Invalid JSON document on line {}'.format(lineno))

def ndjsonProcessor(entity):
  ''''Read application/x-ndjson data into generator request.ndjson.'''
  if not entity.headers.get('Content-Length'):
    raise cherrypy.HTTPError(HTTPStatus.LENGTH_REQUIRED.value)

  cherrypy.serving.request.ndjson = ndjsonGenerator(entity.fp)

@cherrypy.tools.register('before_request_body', priority = 30)
def ndjsonin(content_type):
  request = cherrypy.serving.request
  if isinstance(content_type, str):
      content_type = [content_type]

  for ct in content_type:
      request.body.processors[ct] = ndjsonProcessor


class RecordApi:

  exposed = True


  def HEAD(self, **kwargs):
    filters = self._getFilters(**kwargs)
    group   = kwargs.get('group')
    tz      = kwargs.get('timezone')
    if group and timezone:
      m15Grp = cherrypy.request.app.storage.count(filters, group = True)
      grps, cnts = list(zip(*groupTimeseries(m15Grp, group, tz))) or ['', '']
      cherrypy.response.headers['X-Record-Group'] = ','.join(str(int(v.timestamp())) for v in grps)
      cherrypy.response.headers['X-Record-Count'] = ','.join(map(str, cnts))
    else:
      cherrypy.response.headers['X-Record-Count'] = cherrypy.request.app.storage.count(filters)

    cherrypy.response.headers['Cache-Control'] = 'no-cache'

  @cherrypy.tools.jsonout
  def GET(self, _id = None, **kwargs):
    storage = cherrypy.request.app.storage
    if _id:
      record = storage.get(_id)
      if not record:
        raise cherrypy.HTTPError(HTTPStatus.NOT_FOUND.value)

      cherrypy.response.headers['Cache-Control'] = 'max-age=2600000'  # let cache for ~1 month
      return record.asdict()
    else:
      filters = self._getFilters(**kwargs)
      range = storage.range(int(kwargs['left']), int(kwargs['right']), filters)
      cherrypy.response.headers['Cache-Control'] = 'no-cache'
      return [r.asdict() for r in range]

  @cherrypy.tools.jsonout
  @cherrypy.tools.jsonin(content_type = 'application/json', force = False)
  @cherrypy.tools.ndjsonin(content_type = 'application/x-ndjson')
  def POST(self, **kwargs):
    raw = int(kwargs.get('raw', 0))
    if cherrypy.request.body.type.value == 'application/x-www-form-urlencoded':
      record = createRecord(cherrypy.request.body.params.copy(), raw = raw, parse = True)
    elif cherrypy.request.body.type.value == 'application/json':
      record = createRecord(cherrypy.request.json.copy(), raw = raw)
    elif cherrypy.request.body.type.value == 'application/x-ndjson':
      ids = []
      try:
        for logdicts in chunk(cherrypy.request.ndjson, cherrypy.config['ingestion']['chunk_size']):
          records = cherrypy.request.app.storage.record([
            createRecord(d, raw = raw) for d in logdicts])
          ids.extend(r.id for r in records)
      except (ValueError, ModelError, StorageError) as ex:
        logger.exception('Multiline request error')
        if not ids:
          raise cherrypy.HTTPError(HTTPStatus.BAD_REQUEST.value, str(ex))
        else:
          cherrypy.response.status = HTTPStatus.MULTI_STATUS.value
          return {
            'multistatus' : [
              {'status': HTTPStatus.CREATED,     'body': ids},
              {'status': HTTPStatus.BAD_REQUEST, 'body': self._getErrorBody(
                type(ex).__name__, str(ex))}
            ]
          }
      else:
        cherrypy.response.status = HTTPStatus.CREATED.value
        return ids
    else:
      supported = 'application/x-www-form-urlencoded', 'application/json', 'application/x-ndjson'
      raise cherrypy.HTTPError(
        HTTPStatus.UNSUPPORTED_MEDIA_TYPE.value,
        'Supported content types: {}'.format(', '.join(supported)))

    record = cherrypy.request.app.storage.record([record])[0]
    cherrypy.response.status = HTTPStatus.CREATED.value
    return record.asdict()

  @staticmethod
  def _getFilters(**kwargs):
    return {
      'date'  : (parseIso8601(kwargs.get('after')), parseIso8601(kwargs.get('before'))),
      'level' : kwargs.get('level'),
      'name'  : kwargs.get('name'),
      'query' : kwargs.get('query')
    }

  @staticmethod
  def _getErrorBody(type, message):
    return {'error': {'type': type, 'message': message}}

  def _handleUnexpectedError():  # @NoSelf
    extype, exobj, _ = sys.exc_info()

    status = 500
    if isinstance(exobj, (StorageQueryError, ModelError)):
      status = 400

    if cherrypy.request.method == 'HEAD':
      cherrypy.response.headers['X-Error-Type']    = extype.__name__
      cherrypy.response.headers['X-Error-Message'] = str(exobj)
    else:
      cherrypy.response.body = json.dumps(
        RecordApi._getErrorBody(extype.__name__, str(exobj))).encode()

    cherrypy.response.status = status

  def _handleExpectedError(status, message, traceback, version):  # @NoSelf
    extype, _, _ = sys.exc_info()
    return json.dumps(
      RecordApi._getErrorBody(getattr(extype, '__name__', 'unknown'), message)).encode()

  _cp_config = {
    'request.error_response': _handleUnexpectedError,
    'error_page.default'    : _handleExpectedError
  }


def parseIso8601(s):
  if not s:
    return None

  formats = '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ'
  for i, f in enumerate(formats):
    try:
      return datetime.strptime(s, f).replace(tzinfo = timezone.utc)
    except ValueError:
      if i == len(formats) - 1:
        raise ValueError("time data '{}' is not supported".format(s)) from None
      else:
        pass


def chunk(iterable, k):
  '''Split iterable by chunk of k elements, see
  https://docs.python.org/3/library/itertools.html#itertools-recipes'''
  return ((i for i in c if i is not None) for c in itertools.zip_longest(*[iter(iterable)] * k))


class RecordPurgePlugin(Monitor):

  _schedule = None
  _older = None


  def __init__(self, bus):
    self._schedule = schedule.Scheduler()
    self._schedule.every().day.at('00:00').do(self._purge)

    # Zero frequency means no timing thread will be created
    frequency = 0
    retainDays = cherrypy.config['retention']['days']
    if retainDays:
      frequency = 300
      self._older = timedelta(days = float(retainDays))

    super().__init__(bus, self._schedule.run_pending, frequency = frequency)

  def _purge(self):
    count = self.storage.purge(self._older)
    logger.info('Purged records: %s', count)


User = namedtuple('User', ['username', 'roles'])


def authenticate(realm, username, password):
  '''Basic Auth handler'''

  result = False
  try:
    if cherrypy.config['auth']['authfile']:
      if not hasattr(authenticate, '_authdict'):
        with open(cherrypy.config['auth']['authfile']) as f:
          authenticate._authdict = {r['username']: r for r in json.load(f)}

      if username in authenticate._authdict:
        entry = authenticate._authdict[username]
        roles = set(entry['roles'])
        hash = hashlib.pbkdf2_hmac(
          entry['hashname'], password.encode(), entry['salt'].encode(), entry['iterations'])
        result = compare_digest(entry['pbkdf2'], hash.hex())
    else:
      credentials = cherrypy.config['auth']
      roles = set(credentials['roles'])
      result = username == credentials['username'] and password == credentials['password']

    if result:
      cherrypy.serving.request.user = User(username, roles)
  except Exception:
    logging.exception('Authentication error')

  return result


@cherrypy.tools.register('before_handler')
def authorise():
  ruleName = '{app}.{method}'.format(
    app = cherrypy.serving.request.app.root.__class__.__name__,
    method = cherrypy.serving.request.method)

  if not ruleset.test_rule(ruleName, cherrypy.serving.request):
    raise cherrypy.HTTPError(HTTPStatus.FORBIDDEN.value)


def isA(role):
  @rules.predicate
  def predicate(request):
    return role in request.user.roles
  return predicate

@rules.predicate
def isQueryRequest(request):
  return bool(request.params.get('query'))

canReadRecord = isA('basic-reader') & (~isQueryRequest | isA('query-reader'))


# Note that it can't be used in config directly because it's a dict
ruleset = rules.RuleSet()
ruleset['RecordApi.HEAD'] = canReadRecord
ruleset['RecordApi.GET']  = canReadRecord
ruleset['RecordApi.POST'] = isA('writer')


def brotliCompress(body, level):
  import brotli
  compressor = brotli.Compressor(mode = brotli.MODE_TEXT, quality = level)
  for line in body:
    yield compressor.process(line)
  yield compressor.finish()

@cherrypy.tools.register('before_finalize', name = 'brotli', priority = 79)
def brotliTool(compress_level = 4, mime_types = ['text/html', 'text/plain'], debug = False):
  '''Adaptation of ``cherrypy.lib.encoding.gzip`` for Brotli.'''

  request = cherrypy.serving.request
  response = cherrypy.serving.response

  cherrypy.lib.set_vary_header(response, 'Accept-Encoding')

  # Response body is empty (might be a 304 for instance)
  if not response.body:
    return

  # If returning cached content, which should already have been compressed, don't re-compress
  if getattr(request, 'cached', False):
    return

  # If no Accept-Encoding field is present in a request,
  # the server MAY assume that the client will accept any
  # content coding. In this case, if "identity" is one of
  # the available content-codings, then the server SHOULD use
  # the "identity" content-coding, unless it has additional
  # information that a different content-coding is meaningful
  # to the client.
  acceptable = request.headers.elements('Accept-Encoding')
  if not acceptable:
    return

  for coding in acceptable:
    if coding.value == 'identity' and coding.qvalue != 0:
      return

    if coding.value == 'br':
      # brotliApply(coding, response, mime_types, compress_level, debug)
      if coding.qvalue == 0:
        return

      ct = response.headers.get('Content-Type', '').split(';')[0]
      if ct not in mime_types:
        return

      # Return a generator that compresses the response body
      response.headers['Content-Encoding'] = 'br'
      # Prevent gzip tool from re-compressing the body
      del request.headers['Accept-Encoding']

      response.body = brotliCompress(response.body, compress_level)
      if 'Content-Length' in response.headers:
        # Delete Content-Length header so finalize() recalcs it
        del response.headers['Content-Length']

      return


import sys
import json
import time
import types
import base64
import tempfile
import contextlib
import logging.handlers
from urllib.parse import urlencode
from unittest import mock, TestCase
from datetime import datetime, timedelta, timezone

# CherryPy helper uses nose as runner, emulate for standard runner
sys.modules['nose'] = types.ModuleType('nose')
from cherrypy.test.helper import CPWebCase  # noqa: E402
import cherrypy.lib  # noqa: E402

from .. import test, controller, model  # noqa: E402


delattr(CPWebCase, 'test_gc')

class TestController(CPWebCase):

  interactive = False

  maxDiff = None


  def setUp(self):
    # Proxy nose's setup
    self.setup_class()

  @classmethod
  def setup_server(cls):
    test.setUpModule()

  def tearDown(self):
    # Proxy nose's teardown
    self.teardown_class()


class TestRecordApi(TestController):

  def setUp(self):
    super().setUp()

    cherrypy.tree.apps['/api/v1/record'].storage._db.cursor().execute('TRUNCATE record')

  def getLogRecordDict(self):
    return {
      'lineno'          : 10,
      'thread'          : 140550102431488,
      'levelno'         : 20,
      'msecs'           : 63.5066032409668,
      'levelname'       : 'INFO',
      'lisfor'          : 'lightfullness',
      'nested'          : [{1: 2}, ('123', '234')],
      'stack_info'      : None,
      'threadName'      : 'MainThread',
      'filename'        : 'log.py',
      'exc_text'        : None,
      'module'          : 'log',
      'relativeCreated' : 11.342048645019531,
      'msg'             : 'Band – %d, %s',
      'processName'     : 'MainProcess',
      'created'         : 1497106862.0635066,
      'funcName'        : 'info',
      'args'            : (8, 'arg2'),
      'asctime'         : '2017-06-10 17:01:02,063',
      'exc_info'        : None,
      'message'         : 'Band – 8, arg2',
      'foo'             : 'bar',
      'process'         : 29799,
      'pathname'        : 'log.py',
      'name'            : 'test'
    }

  def testPostInfoUrlencoded(self):
    body = urlencode(self.getLogRecordDict())
    headers = [
      ('content-type',   'application/x-www-form-urlencoded'),
      ('content-length', str(len(body)))
    ]

    self.getPage('/api/v1/record', method = 'post', body = body, headers = headers)
    self.assertStatus(201)
    bodyPost = json.loads(self.body.decode())

    self.getPage('/api/v1/record/{}'.format(bodyPost['id']))
    self.assertStatus(200)
    self.assertHeader('Cache-Control', 'max-age=2600000')
    bodyGet = json.loads(self.body.decode())
    self.assertEqual(bodyPost, bodyGet)

    self.assertEqual({
      'level'   :  20,
      'ts'      : '2017-06-10 15:01:02.063507+00:00',
      'name'    : 'test',
      'message' : 'Band – 8, arg2',
      'id'      : bodyPost['id'],
      'logrec'  : {
        'meta' : {
          'lineno'          : 10,
          'msecs'           : 63.5066032409668,
          'processName'     : 'MainProcess',
          'relativeCreated' : 11.342048645019531,
          'thread'          : 140550102431488,
          'filename'        : 'log.py',
          'msg'             : 'Band – %d, %s',
          'threadName'      : 'MainThread',
          'args'            : [8, 'arg2'],
          'module'          : 'log',
          'process'         : 29799,
          'funcName'        : 'info',
          'pathname'        : 'log.py',
          'stack_info'      : None
        },
        'data' : {
          'foo'    : 'bar',
          'lisfor' : 'lightfullness',
          'nested' : [{'1': 2}, ['123', '234']],
        }
      }
    }, bodyGet)

  def testPostErrorUrlencoded(self):
    logrec = {
      'lineno'          : '16',
      'thread'          : '140550102431488',
      'levelno'         : '40',
      'msecs'           : '97.8283882141113',
      'levelname'       : 'ERROR',
      'pathname'        : 'log.py',
      'stack_info'      : 'None',
      'threadName'      : 'MainThread',
      'filename'        : 'log.py',
      'module'          : 'log',
      'relativeCreated' : '45.66383361816406',
      'msg'             : 'Failure %s',
      'processName'     : 'MainProcess',
      'created'         : '1497106862.0978284',
      'funcName'        : 'error',
      'args'            : '(123,)',
      'asctime'         : '2017-06-10 17:01:02,097',
      'message'         : 'Failure 123',
      'process'         : '29799',
      'name'            : 'test',
      'exc_text'        :
        'Traceback (most recent call last):\n'
        '  File "log.py", line 72, in <module>\n    1 / 0\n'
        'ZeroDivisionError: division by zero',
      'exc_info' :
        "(<class 'ZeroDivisionError'>, "
        "ZeroDivisionError('division by zero',), <traceback object at 0x7fd45c98b248>)",
    }
    body = urlencode(logrec)
    headers = [
      ('content-type',   'application/x-www-form-urlencoded'),
      ('content-length', str(len(body)))
    ]

    self.getPage('/api/v1/record', method = 'post', body = body, headers = headers)
    self.assertStatus(201)
    bodyPost = json.loads(self.body.decode())

    self.getPage('/api/v1/record/{}'.format(bodyPost['id']))
    self.assertStatus(200)
    bodyGet = json.loads(self.body.decode())
    self.assertEqual(bodyPost, bodyGet)

    self.assertEqual({
      'level'   : 40,
      'name'    : 'test',
      'id'      : bodyGet['id'],
      'message' : 'Failure 123',
      'ts'      : '2017-06-10 15:01:02.097828+00:00',
      'logrec'  : {
        'meta' : {
          'thread'          : 140550102431488,
          'process'         : 29799,
          'processName'     : 'MainProcess',
          'args'            : [123],
          'funcName'        : 'error',
          'lineno'          : 16,
          'filename'        : 'log.py',
          'threadName'      : 'MainThread',
          'msecs'           : 97.8283882141113,
          'module'          : 'log',
          'msg'             : 'Failure %s',
          'relativeCreated' : 45.66383361816406,
          'pathname'        : 'log.py',
          'stack_info'      : None,
        },
        'error' : {
          'exc_text' :
            'Traceback (most recent call last):\n  '
            'File "log.py", line 72, in <module>\n    1 / 0\nZeroDivisionError: division by zero',
          'exc_info' :
            "(<class 'ZeroDivisionError'>, ZeroDivisionError('division by zero',), "
            "<traceback object at 0x7fd45c98b248>)",
        }
      },
    }, bodyGet)

  def testPostUnsupportedMediaType(self):
    body = 'The Lung'
    headers = [
      ('content-type',   'text/plain'),
      ('content-length', str(len(body)))
    ]
    self.getPage('/api/v1/record', method = 'post', body = body, headers = headers)
    self.assertStatus(415)

  def testPostInfoJson(self):
    body = json.dumps(self.getLogRecordDict())
    headers = [
      ('content-type',   'application/json'),
      ('content-length', str(len(body)))
    ]
    self.getPage('/api/v1/record', method = 'post', body = body, headers = headers)
    self.assertStatus(201)
    bodyPost = json.loads(self.body.decode())

    self.getPage('/api/v1/record/{}'.format(bodyPost['id']))
    self.assertStatus(200)
    self.assertHeader('Cache-Control', 'max-age=2600000')
    bodyGet = json.loads(self.body.decode())
    self.assertEqual(bodyPost, bodyGet)

    self.assertEqual({
      'level'   :  20,
      'ts'      : '2017-06-10 15:01:02.063507+00:00',
      'name'    : 'test',
      'message' : 'Band – 8, arg2',
      'id'      : bodyPost['id'],
      'logrec'  : {
        'meta' : {
          'lineno'          : 10,
          'msecs'           : 63.5066032409668,
          'processName'     : 'MainProcess',
          'relativeCreated' : 11.342048645019531,
          'thread'          : 140550102431488,
          'filename'        : 'log.py',
          'msg'             : 'Band – %d, %s',
          'threadName'      : 'MainThread',
          'args'            : [8, 'arg2'],
          'module'          : 'log',
          'process'         : 29799,
          'funcName'        : 'info',
          'pathname'        : 'log.py',
          'stack_info'      : None
        },
        'data' : {
          'foo'    : 'bar',
          'lisfor' : 'lightfullness',
          'nested' : [{'1': 2}, ['123', '234']],
        }
      }
    }, bodyGet)

  def testPostRawJson(self):
    body = json.dumps({'a': 1, 'b': [2], 'c': '3'})
    headers = [
      ('content-type',   'application/json'),
      ('content-length', str(len(body)))
    ]
    self.getPage('/api/v1/record?raw=1', method = 'post', body = body, headers = headers)
    self.assertStatus(201)
    bodyPost = json.loads(self.body.decode())

    self.getPage('/api/v1/record/{}'.format(bodyPost['id']))
    self.assertStatus(200)
    self.assertHeader('Cache-Control', 'max-age=2600000')
    bodyGet = json.loads(self.body.decode())
    self.assertEqual(bodyPost, bodyGet)

    self.assertEqual({
      'level'   :  20,
      'ts'      : bodyPost['ts'],
      'name'    : '',
      'message' : '',
      'id'      : bodyPost['id'],
      'logrec'  : {'a': 1, 'b': [2], 'c': '3'},
    }, bodyGet)

  def testPostIncompleteLogRecord(self):
    body = json.dumps({})
    headers = [
      ('content-type',   'application/json'),
      ('content-length', str(len(body)))
    ]
    with self.assertLogs('cherrypy.error', 'ERROR'):
      self.getPage('/api/v1/record?raw=0', method = 'post', body = body, headers = headers)
    self.assertStatus(400)
    actual = json.loads(self.body.decode())
    self.assertEqual(
      {'error': {'message': 'Key "name" is missing', 'type': 'ModelError'}}, actual)

  def testPostInfoMultilineJson(self):
    logdict = self.getLogRecordDict()
    del logdict['args'], logdict['nested']

    logdicts = [logdict] * 2
    body = '\n'.join(map(json.dumps, logdicts))
    headers = [
      ('content-type',   'application/x-ndjson'),
      ('content-length', str(len(body)))
    ]
    self.getPage('/api/v1/record', method = 'post', body = body, headers = headers)
    self.assertStatus(201)
    actual = json.loads(self.body.decode())
    self.assertEqual(2, len(actual))

    for i, id in enumerate(actual):
      self.getPage('/api/v1/record/{}'.format(id))
      actual = model.Record(**json.loads(self.body.decode()))
      actual.ts = controller.parseIso8601(actual.ts.replace(' ', 'T').replace('+00:00', 'Z'))
      expected = model.createRecord(logdicts[i].copy())
      expected.id = id
      self.assertEqual(dict(expected.asdict()), dict(actual.asdict()))

  def testPostInfoMultilineMalformedJson(self):
    logdict = self.getLogRecordDict()
    logdicts = [logdict] * 2
    body = '\n'.join(map(json.dumps, logdicts)) + '\n!@#'
    headers = [
      ('content-type',   'application/x-ndjson'),
      ('content-length', str(len(body)))
    ]
    with self.assertLogs('chronologer.controller', 'ERROR'):
      self.getPage('/api/v1/record', method = 'post', body = body, headers = headers)
    self.assertStatus(400)
    actual = json.loads(self.body.decode())
    self.assertEqual(
      {'error': {'type': 'HTTPError', 'message': 'Invalid JSON document on line 3'}}, actual)

    self.getPage('/api/v1/record', method = 'HEAD')
    self.assertStatus(200)
    self.assertEqual(0, int(dict(self.headers)['X-Record-Count']))

  def testPostInfoMultilineMultistatusJson(self):
    logdict = self.getLogRecordDict()
    chunkSize = cherrypy.config['ingestion']['chunk_size']
    logdicts = [logdict] * chunkSize
    body = '\n'.join(map(json.dumps, logdicts)) + '\n!@#'
    headers = [
      ('content-type',   'application/x-ndjson'),
      ('content-length', str(len(body)))
    ]
    with self.assertLogs('chronologer.controller', 'ERROR'):
      self.getPage('/api/v1/record', method = 'post', body = body, headers = headers)
    self.assertStatus(207)
    actual = json.loads(self.body.decode())
    self.assertEqual(
      {'multistatus': [
        {
          'status' : 201,
          'body'   : list(range(1, chunkSize + 1))},
        {
          'status' : 400,
          'body'   : {
            'error': {
              'message' : 'Invalid JSON document on line {}'.format(chunkSize + 1),
              'type'    : 'ValueError'
            }
          }
        },
      ]}, actual)

    self.getPage('/api/v1/record', method = 'HEAD')
    self.assertStatus(200)
    self.assertEqual(chunkSize, int(dict(self.headers)['X-Record-Count']))

  def testPostRawMultilineJson(self):
    logdict = self.getLogRecordDict()
    del logdict['args'], logdict['nested']

    logdicts = [logdict] * 2
    body = '\n'.join(map(json.dumps, logdicts))
    headers = [
      ('content-type',   'application/x-ndjson'),
      ('content-length', str(len(body)))
    ]
    self.getPage('/api/v1/record?raw=1', method = 'post', body = body, headers = headers)
    self.assertStatus(201)
    actual = json.loads(self.body.decode())
    self.assertEqual(2, len(actual))

    for i, id in enumerate(actual):
      self.getPage('/api/v1/record/{}'.format(id))
      self.assertEqual(logdicts[i], json.loads(self.body.decode())['logrec'])

  def testHttpHandler(self):
    logger = logging.getLogger('{}.testHttpHandler'.format(__name__))
    logger.propagate = False
    logger.level = logging.INFO
    logger.addHandler(logging.handlers.HTTPHandler(
      host   = 'localhost:{}'.format(self.PORT),
      url    = '/api/v1/record',
      method = 'POST'
    ))

    now = datetime.now(timezone.utc).replace(microsecond = 0)

    logger.info('Test', extra = {'lisfor': 'lighty'})

    self.getPage('/api/v1/record', method = 'HEAD')
    self.assertStatus(200)
    self.assertEqual(1, int(dict(self.headers)['X-Record-Count']))
    self.assertHeader('Cache-Control', 'no-cache')

    try:
      1 / 0
    except Exception:
      logger.exception('Failure', extra = {'lisfor': 'twiggy'})

    self.getPage('/api/v1/record', method = 'HEAD')
    self.assertStatus(200)
    self.assertEqual(2, int(dict(self.headers)['X-Record-Count']))

    self.getPage('/api/v1/record?level=30&name=chronologer', method = 'HEAD')
    self.assertStatus(200)
    self.assertEqual(1, int(dict(self.headers)['X-Record-Count']))

    self.getPage('/api/v1/record?left=0&right=1')
    self.assertStatus(200)
    actual = json.loads(self.body.decode())

    for item in actual:
      self.assertAlmostEqual(
        now,
        datetime.strptime(
          item.pop('ts').rsplit('+', 1)[0], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo = timezone.utc),
        delta = timedelta(seconds = 2))

      list(map(
        item['logrec']['meta'].pop, ('lineno', 'msecs', 'process', 'relativeCreated', 'thread')))

      self.assertTrue(
        item['logrec']['meta'].pop('pathname').endswith('chronologer/test/controller.py'))

    expected = [{
      'name'    : 'chronologer.test.controller.testHttpHandler',
      'id'      : 2,
      'level'   : logging.ERROR,
      'message' : 'Failure',
      'logrec'  : {
        'data': {'lisfor': 'twiggy'},
        'meta': {
          'args': [],
          'filename': 'controller.py',
          'funcName': 'testHttpHandler',
          'module': 'controller',
          'msg': 'Failure',
          'processName': 'MainProcess',
          'stack_info': None,
          'threadName': 'MainThread'
        }
      },
    }, {
      'name'    : 'chronologer.test.controller.testHttpHandler',
      'id'      : 1,
      'level'   : logging.INFO,
      'message' : 'Test',
      'logrec'  : {
        'data': {'lisfor': 'lighty'},
        'meta': {
          'args': [],
          'filename': 'controller.py',
          'funcName': 'testHttpHandler',
          'module': 'controller',
          'msg': 'Test',
          'processName': 'MainProcess',
          'stack_info': None,
          'threadName': 'MainThread'
        }
      },
    }]
    self.assertEqual(expected, actual)

    params = {
      'left'   : 0,
      'right'  : 0,
      'after'  : (now.replace(tzinfo = None) - timedelta(seconds = 5)).isoformat() + 'Z',
      'before' : (now.replace(tzinfo = None) + timedelta(seconds = 5)).isoformat() + 'Z',
      'name'   : 'chronologer',
      'level'  : logging.ERROR,
      'query'  : "logrec->>'$.data.lisfor' = 'twiggy'",
    }
    self.getPage('/api/v1/record?' + urlencode(params))
    self.assertStatus(200)
    self.assertHeader('Cache-Control', 'no-cache')
    actual = json.loads(self.body.decode())
    self.assertAlmostEqual(
      now,
      datetime
        .strptime(actual[0].pop('ts').rsplit('+', 1)[0], '%Y-%m-%d %H:%M:%S.%f')
        .replace(tzinfo = timezone.utc),
      delta = timedelta(seconds = 2))
    list(map(
      actual[0]['logrec']['meta'].pop,
      ('lineno', 'msecs', 'process', 'relativeCreated', 'thread')))
    self.assertTrue(
      actual[0]['logrec']['meta'].pop('pathname').endswith('chronologer/test/controller.py'))
    self.assertEqual(expected[:1], actual)

  def testCountHistorgram(self):
    logger = logging.getLogger('{}.testCountHistorgram'.format(__name__))
    logger.propagate = False
    logger.level = logging.INFO
    logger.addHandler(logging.handlers.HTTPHandler(
      host   = 'localhost:{}'.format(self.PORT),
      url    = '/api/v1/record',
      method = 'POST'
    ))

    now = datetime(2017, 6, 17, 23, 14, 37, tzinfo = timezone.utc)
    for i in range(4):
      with mock.patch('time.time', lambda: (now - timedelta(hours = i)).timestamp()):
        logger.info('Test', extra = {'i': i})

    qs = urlencode({'group': 'hour', 'timezone': 'Europe/Amsterdam'})
    self.getPage('/api/v1/record?' + qs, method = 'HEAD')
    self.assertStatus(200)
    self.assertHeader('X-Record-Count', '1,1,1,1')
    self.assertHeader('X-Record-Group', ','.join([
      '1497729600', '1497733200', '1497736800', '1497740400']))

    qs = urlencode({'group': 'day', 'timezone': 'Europe/Amsterdam'})
    self.getPage('/api/v1/record?' + qs, method = 'HEAD')
    self.assertStatus(200)
    self.assertHeader('X-Record-Count', '2,2')
    self.assertHeader('X-Record-Group', ','.join(['1497650400', '1497736800']))

    qs = urlencode({'group': 'hour', 'timezone': 'Europe/Amsterdam', 'level': logging.ERROR})
    self.getPage('/api/v1/record?' + qs, method = 'HEAD')
    self.assertStatus(200)
    self.assertHeader('X-Record-Count', '')
    self.assertHeader('X-Record-Group', '')

  def testRecordCountError(self):
    with self.assertLogs('cherrypy.error', 'ERROR') as ctx:
      self.getPage('/api/v1/record?' + urlencode({'query': '123#'}), method = 'HEAD')
    self.assertStatus(400)
    self.assertBody(b'')
    self.assertHeader('X-Error-Type', 'StorageQueryError')
    self.assertHeader('X-Error-Message', 'Make sure the query filter is a valid WHERE expression')

    self.assertEqual(1, len(ctx.output))
    self.assertTrue(ctx.output[0].endswith(
      'chronologer.storage.StorageQueryError: '
      'Make sure the query filter is a valid WHERE expression'))

  def testRecordRangeError(self):
    with self.assertLogs('cherrypy.error', 'ERROR') as ctx:
      self.getPage('/api/v1/record?' + urlencode({'query': '123#', 'left': 0, 'right': 127}))
    self.assertStatus(400)
    self.assertHeader('Content-Type', 'application/json')
    self.assertEqual({'error': {
      'message' : 'Make sure the query filter is a valid WHERE expression',
      'type'    : 'StorageQueryError'
    }}, json.loads(self.body.decode()))

    self.assertEqual(1, len(ctx.output))
    self.assertTrue(ctx.output[0].endswith(
      'chronologer.storage.StorageQueryError: '
      'Make sure the query filter is a valid WHERE expression'))

  def testRecordNotFound(self):
    self.getPage('/api/v1/record/-1')
    self.assertStatus(404)
    self.assertHeader('Content-Type', 'application/json')
    self.assertEqual({'error': {
      'message' : 'Nothing matches the given URI',
      'type'    : 'HTTPError'
    }}, json.loads(self.body.decode()))


class TestRecordApiAuthorisation(TestController):

  authHeaders = None


  def setUp(self):
    super().setUp()

    credentials = base64.b64encode(
      '{}:{}'.format(
        cherrypy.config['auth']['username'],
        cherrypy.config['auth']['password']
      ).encode()).decode()
    self.authHeaders = [
      ('Authorization', 'Basic {}'.format(credentials))]

    m = mock.patch.dict(controller.RecordApi._cp_config, {
      'tools.auth_basic.on'            : True,
      'tools.auth_basic.realm'         : 'Test',
      'tools.auth_basic.checkpassword' : controller.authenticate,
      'tools.authorise.on'             : True,
    })
    m.__enter__()
    self.addCleanup(m.__exit__)

  def testHead(self):
    with mock.patch.dict(cherrypy.config['auth'], {'roles': []}):
      self.getPage('/api/v1/record', method = 'HEAD', headers = self.authHeaders.copy())
      self.assertStatus(403)
      self.getPage('/api/v1/record?query=1', method = 'HEAD', headers = self.authHeaders.copy())
      self.assertStatus(403)

    with mock.patch.dict(cherrypy.config['auth'], {'roles': ['writer']}):
      self.getPage('/api/v1/record', method = 'HEAD', headers = self.authHeaders.copy())
      self.assertStatus(403)
      self.getPage('/api/v1/record?query=1', method = 'HEAD', headers = self.authHeaders.copy())
      self.assertStatus(403)

    with mock.patch.dict(cherrypy.config['auth'], {'roles': ['basic-reader']}):
      self.getPage('/api/v1/record', method = 'HEAD', headers = self.authHeaders.copy())
      self.assertStatus(200)
      self.getPage('/api/v1/record?query=1', method = 'HEAD', headers = self.authHeaders.copy())
      self.assertStatus(403)

    with mock.patch.dict(cherrypy.config['auth'], {'roles': ['basic-reader', 'query-reader']}):
      self.getPage('/api/v1/record', method = 'HEAD', headers = self.authHeaders.copy())
      self.assertStatus(200)
      self.getPage('/api/v1/record?query=1', method = 'HEAD', headers = self.authHeaders.copy())
      self.assertStatus(200)

  def testGet(self):
    with mock.patch.dict(cherrypy.config['auth'], {'roles': []}):
      self.getPage('/api/v1/record/1', method = 'GET', headers = self.authHeaders.copy())
      self.assertStatus(403)
      self.getPage('/api/v1/record/1?query=1', method = 'GET', headers = self.authHeaders.copy())
      self.assertStatus(403)

    with mock.patch.dict(cherrypy.config['auth'], {'roles': ['writer']}):
      self.getPage('/api/v1/record/1', method = 'GET', headers = self.authHeaders.copy())
      self.assertStatus(403)
      self.getPage('/api/v1/record/1?query=1', method = 'GET', headers = self.authHeaders.copy())
      self.assertStatus(403)

    with mock.patch.dict(cherrypy.config['auth'], {'roles': ['basic-reader']}):
      self.getPage('/api/v1/record/1', method = 'GET', headers = self.authHeaders.copy())
      self.assertStatus(404)
      self.getPage('/api/v1/record/1?query=1', method = 'GET', headers = self.authHeaders.copy())
      self.assertStatus(403)

    with mock.patch.dict(cherrypy.config['auth'], {'roles': ['basic-reader', 'query-reader']}):
      self.getPage('/api/v1/record/1', method = 'GET', headers = self.authHeaders.copy())
      self.assertStatus(404)
      self.getPage('/api/v1/record/1?query=1', method = 'GET', headers = self.authHeaders.copy())
      self.assertStatus(404)

  def testPost(self):
    with mock.patch.dict(cherrypy.config['auth'], {'roles': []}):
      self.getPage('/api/v1/record', method = 'POST', headers = self.authHeaders.copy())
      self.assertStatus(403)

    with mock.patch.dict(cherrypy.config['auth'], {'roles': ['writer']}):
      with self.assertLogs('cherrypy.error', 'ERROR'):
        self.getPage('/api/v1/record', method = 'POST', headers = self.authHeaders.copy())
      self.assertStatus(400)

    with mock.patch.dict(cherrypy.config['auth'], {'roles': ['basic-reader']}):
      self.getPage('/api/v1/record', method = 'POST', headers = self.authHeaders.copy())
      self.assertStatus(403)

    with mock.patch.dict(cherrypy.config['auth'], {'roles': ['basic-reader', 'query-reader']}):
      self.getPage('/api/v1/record', method = 'POST', headers = self.authHeaders.copy())
      self.assertStatus(403)


class TestRecordPurgePlugin(TestCase):

  setUpClass = test.setUpModule

  def testNoRetentionDays(self):
    self.assertIsNone(cherrypy.config['retention']['days'])
    testee = controller.RecordPurgePlugin(cherrypy.engine)
    testee.start()
    try:
      self.assertIsNone(testee.thread)
    finally:
      testee.stop()

  def testRetentionDaysDefined(self):
    cherrypy.config['retention']['days'] = 1
    with mock.patch.object(controller.RecordPurgePlugin, '_purge') as purge:
      testee = controller.RecordPurgePlugin(cherrypy.engine)
      nextRun = testee._schedule.next_run
      testee.frequency = 0.1
      with mock.patch('schedule.datetime') as m:
        m.datetime.now.return_value = nextRun + timedelta(seconds = 1)
        testee.start()
        try:
          time.sleep(0.11)
          purge.assert_called_once_with()
          self.assertIsNotNone(testee.thread)
        finally:
          testee.stop()


class TestAuthenticate(TestCase):

  setUpClass = test.setUpModule

  def tearDown(self):
    # In web request's context ``cherrypy.request`` is bound to the request
    with contextlib.suppress(AttributeError):
      del cherrypy.request.user

  def testFromEnv(self):
    authconf = {'username': 'bob', 'password': 'obb', 'roles': ['a', 'b']}
    with mock.patch.dict(cherrypy.config['auth'], authconf):
      self.assertFalse(controller.authenticate('Realm', 'alice', ''))
      self.assertFalse(hasattr(cherrypy.request, 'user'))

      self.assertFalse(controller.authenticate('Realm', 'bob', ''))
      self.assertFalse(hasattr(cherrypy.request, 'user'))

      self.assertTrue(controller.authenticate('Realm', 'bob', 'obb'))
      self.assertEqual('bob', cherrypy.request.user.username)
      self.assertEqual({'a', 'b'}, cherrypy.request.user.roles)

  def testFromFile(self):
    with tempfile.NamedTemporaryFile('w') as fp:
      json.dump([
        {
          'username': 'bob',
          'pbkdf2': 'f57ef1e3e8f90cb367dedd44091f251b5b15c9c36ddd7923731fa7ee41cbaa82',
          'hashname': 'sha256',
          'salt': 'c0139cff',
          'iterations': 32,
          'roles': ['a', 'b']
        }, {
          'username': 'obo',
          'pbkdf2': (
            'ff680a9237549f698da5345119dec1ed314eb4fdefe59837d0724d747c3169'
            '089ae45215ec98b7c84b7b8b3ac1589139'),
          'hashname': 'sha384',
          'salt': '9230dbdd5a13f009',
          'iterations': 4096,
          'roles': ['c', 'd']
        },
      ], fp)
      fp.flush()

      authconf = {'authfile': fp.name}
      with mock.patch.dict(cherrypy.config['auth'], authconf):
        self.assertFalse(controller.authenticate('Realm', 'alice', ''))
        self.assertFalse(hasattr(cherrypy.request, 'user'))

        self.assertEqual(2, len(controller.authenticate._authdict))

        self.assertFalse(controller.authenticate('Realm', 'bob', ''))
        self.assertFalse(hasattr(cherrypy.request, 'user'))

        self.assertTrue(controller.authenticate('Realm', 'bob', 'obo'))
        self.assertEqual('bob', cherrypy.request.user.username)
        self.assertEqual({'a', 'b'}, cherrypy.request.user.roles)

        self.assertTrue(controller.authenticate('Realm', 'obo', 'bob'))
        self.assertEqual('obo', cherrypy.request.user.username)
        self.assertEqual({'c', 'd'}, cherrypy.request.user.roles)


class TestCompression(TestController):

  def setUp(self):
    super().setUp()

    m = mock.patch.dict(controller.RecordApi._cp_config, {
      'tools.gzip.on'           : True,
      'tools.gzip.mime_types'   : ['application/json', 'application/javascript'],
      'tools.brotli.on'         : True,
      'tools.brotli.mime_types' : ['application/json', 'application/javascript'],
    })
    m.__enter__()
    self.addCleanup(m.__exit__)

  def testIdentity(self):
    headerList = [
      {},
      {'Accept-Encoding': 'identity'},
      {'Accept-Encoding': 'identity, gzip'},
      {'Accept-Encoding': 'identity, br'},
      {'Accept-Encoding': 'identity, gzip, br'},
    ]
    for requestHeaders in headerList:
      self.getPage('/api/v1/record/1', headers = list(requestHeaders.items()))
      self.assertStatus(404)
      self.assertEqual(
        {'error': {'message': 'Nothing matches the given URI', 'type': 'HTTPError'}},
        json.loads(self.body.decode()))

      responseHeaders = dict(self.headers)
      self.assertNotIn('Content-Encoding', responseHeaders)
      self.assertEqual(513, int(responseHeaders['Content-Length']))
      self.assertEqual('Accept-Encoding', responseHeaders['Vary'])
      self.assertEqual('application/json', responseHeaders['Content-Type'])

  def testGzip(self):
    self.getPage('/api/v1/record/1', headers = [('Accept-Encoding', 'gzip')])
    self.assertStatus(404)
    self.assertEqual(
        {'error': {'message': 'Nothing matches the given URI', 'type': 'HTTPError'}},
        json.loads(cherrypy.lib.encoding.decompress(self.body).decode()))

    responseHeaders = dict(self.headers)
    self.assertEqual(93, int(responseHeaders['Content-Length']))
    self.assertEqual('gzip', responseHeaders['Content-Encoding'])
    self.assertEqual('Accept-Encoding', responseHeaders['Vary'])
    self.assertEqual('application/json', responseHeaders['Content-Type'])

  def testBrotli(self):
    import brotli

    headerList = [{'Accept-Encoding': 'br'}, {'Accept-Encoding': 'gzip, br'}]
    for requestHeaders in headerList:
      self.getPage('/api/v1/record/1', headers = list(requestHeaders.items()))
      self.assertStatus(404)
      self.assertEqual(
          {'error': {'message': 'Nothing matches the given URI', 'type': 'HTTPError'}},
          json.loads(brotli.decompress(self.body).decode()))

      responseHeaders = dict(self.headers)
      self.assertTrue(69 <= int(responseHeaders['Content-Length']) <= 71)
      self.assertEqual('br', responseHeaders['Content-Encoding'])
      self.assertEqual('Accept-Encoding', responseHeaders['Vary'])
      self.assertEqual('application/json', responseHeaders['Content-Type'])


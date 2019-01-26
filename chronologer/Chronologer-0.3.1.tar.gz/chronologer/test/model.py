import sys
import queue
import unittest
import logging.handlers
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode, parse_qsl

from . import setUpModule  # noqa: F401 @UnusedImport
from ..model import createRecord, groupTimeseries


class TestExceptionData(unittest.TestCase):

  record = None
  '''Logging record under test'''


  def setUp(self):
    with self.assertLogs('', logging.ERROR) as ctx:
      try:
        1 / 0
      except ZeroDivisionError:
        logging.exception('Thou hast ill math')
    self.record = ctx.records[0]

  def testExceptionHttpHandlerDirectly(self):
    # see ``HTTPHandler.mapLogRecord`` and ``HTTPHandler.emit``
    postData = urlencode(self.record.__dict__)
    actual = createRecord(dict(parse_qsl(postData)), parse = True)

    self.assertEqual('root', actual.name)
    self.assertEqual(logging.ERROR, actual.level)
    self.assertEqual('Thou hast ill math', actual.message)
    self.assertAlmostEqual(datetime.now(timezone.utc), actual.ts, delta = timedelta(seconds = 1))

    self.assertTrue(actual.logrec['error']['exc_info'].startswith(
      "(<class 'ZeroDivisionError'>, ZeroDivisionError('division by zero'"))
    self.assertTrue(actual.logrec['error']['exc_text'].startswith(
      'Traceback (most recent call last):'))
    self.assertTrue(actual.logrec['error']['exc_text'].endswith(
      'ZeroDivisionError: division by zero'))

  def testExceptionViaQueueHandler(self):
    q = queue.Queue()
    h = logging.handlers.QueueHandler(q)
    h.emit(self.record)
    record = q.get_nowait()

    # see ``HTTPHandler.mapLogRecord`` and ``HTTPHandler.emit``
    postData = urlencode(record.__dict__)
    actual = createRecord(dict(parse_qsl(postData)), parse = True)

    self.assertEqual('root', actual.name)
    self.assertEqual(logging.ERROR, actual.level)
    self.assertAlmostEqual(datetime.now(timezone.utc), actual.ts, delta = timedelta(seconds = 1))

    # see https://bugs.python.org/issue34334
    if sys.version_info >= (3, 7, 1):
      self.assertTrue(actual.message.startswith('Thou hast ill math\nTraceback'))
      self.assertFalse('error' in actual.logrec)
    else:
      if sys.version_info[:3] == (3, 7, 0):
        self.assertTrue(actual.message.startswith('Thou hast ill math\nTraceback'))
      else:
        self.assertEquals('Thou hast ill math', actual.message)

      self.assertTrue(actual.logrec['error']['exc_info'] is None, 'Stripped by QueueHandler')
      self.assertTrue(actual.logrec['error']['exc_text'].startswith(
        'Traceback (most recent call last):'))
      self.assertTrue(actual.logrec['error']['exc_text'].endswith(
        'ZeroDivisionError: division by zero'))


class TestDateGrouping(unittest.TestCase):

  def testDst(self):
    seq = (
      (datetime(2018, 10, 27, 9,  0,  tzinfo = timezone.utc), 11),
      (datetime(2018, 10, 27, 9,  45, tzinfo = timezone.utc), 11),
      (datetime(2018, 10, 27, 11, 45, tzinfo = timezone.utc), 7),
      (datetime(2018, 10, 27, 12, 30, tzinfo = timezone.utc), 22),
      (datetime(2018, 10, 27, 13, 0,  tzinfo = timezone.utc), 55),
      (datetime(2018, 10, 27, 13, 30, tzinfo = timezone.utc), 44),
      (datetime(2018, 10, 27, 13, 45, tzinfo = timezone.utc), 55),
      (datetime(2018, 10, 27, 23, 45, tzinfo = timezone.utc), 11),
      (datetime(2018, 10, 28, 0,  0,  tzinfo = timezone.utc), 10),
      (datetime(2018, 10, 28, 1,  15, tzinfo = timezone.utc), 11),
      (datetime(2018, 10, 28, 2,  30, tzinfo = timezone.utc), 12),
      (datetime(2018, 10, 28, 8,  0,  tzinfo = timezone.utc), 13),
      (datetime(2018, 10, 28, 8,  15, tzinfo = timezone.utc), 31),
      (datetime(2018, 10, 28, 8,  30, tzinfo = timezone.utc), 11),
      (datetime(2018, 10, 28, 11, 45, tzinfo = timezone.utc), 22),
      (datetime(2018, 10, 28, 12, 15, tzinfo = timezone.utc), 11),
      (datetime(2018, 10, 28, 13, 0,  tzinfo = timezone.utc), 11),
      (datetime(2018, 10, 28, 19, 15, tzinfo = timezone.utc), 11)
    )

    actual = list(groupTimeseries(seq, 'day', 'Europe/Amsterdam'))
    tz = actual[0][0].tzinfo
    self.assertEqual('CEST', tz.tzname(datetime(2018, 10, 27, 0, 0)))
    self.assertEqual([
      (datetime(2018, 10, 27, 0, 0, tzinfo = tz), 205),
      (datetime(2018, 10, 28, 0, 0, tzinfo = tz), 154)
    ], actual)


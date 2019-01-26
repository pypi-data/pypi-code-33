import queue
import unittest
import logging.handlers
from unittest import mock

from . import setUpModule  # noqa: F401 @UnusedImport
from ..client import QueueProxyHandler


class TestQueueProxyHandler(unittest.TestCase):

  testee = None
  logger = None


  def setUp(self):
    q = queue.Queue(8)
    self.testee = QueueProxyHandler(q, logging.handlers.BufferingHandler, capacity = 1024)

    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)
    self.logger.propagate = False
    self.logger.handlers = [self.testee]

  def testLog(self):
    self.logger.info('Foo %s', 'bar', extra = {'struct': 'LOL'})

    self.testee.queue.join()
    self.assertEqual(1, len(self.testee._listener.handlers[0].buffer))

    record = self.testee._listener.handlers[0].buffer[0]
    self.assertEqual('INFO', record.levelname)
    self.assertEqual('Foo bar', record.message)
    self.assertEqual('LOL', record.struct)

  def testLogQueueFull(self):
    self.testee._listener.stop()
    for _ in range(8):
      self.logger.info('Excessive logging', extra = {'struct': 'LOL'})

    with mock.patch('logging.sys.stderr') as m:
      self.logger.info('Excessive logging', extra = {'struct': 'LOL'})
    message = ''.join(v[0][0] for v in m.write.call_args_list)
    self.assertIn('queue.Full', message)
    self.assertIn('Excessive logging', message)

    self.testee._listener.start()

  def testLoggerNamePrefix(self):
    testee = QueueProxyHandler(
      self.testee.queue, logging.handlers.BufferingHandler, capacity = 8, prefix = 'appname')
    self.logger.handlers = [testee]
    self.logger.warning('Logging NIH')

    self.testee.queue.join()
    self.assertEqual(1, len(self.testee._listener.handlers[0].buffer))

    record = self.testee._listener.handlers[0].buffer[0]
    self.assertEqual('appname.chronologer.test.client', record.name)

  def testLoggerNameSuffix(self):
    testee = QueueProxyHandler(
      self.testee.queue, logging.handlers.BufferingHandler, capacity = 8, prefix = 'appname')
    self.logger.handlers = [testee]
    self.logger.warning('Logging NIH', extra = {'suffix': 'classname'})

    self.testee.queue.join()
    self.assertEqual(1, len(self.testee._listener.handlers[0].buffer))

    record = self.testee._listener.handlers[0].buffer[0]
    self.assertEqual('appname.chronologer.test.client.classname', record.name)


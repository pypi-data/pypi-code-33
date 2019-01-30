import unittest

from cpbox.app import eventlog
from cpbox.app import appconfig
from datetime import datetime
from cpbox.tool import logger
import time

class TestToolUtils(unittest.TestCase):

    def setUp(self):
        logger.make_logger('test-event-log', 'debug', 'localhost', True)

    def test_event_log(self):
        for i in range(1, 10):
            payload = {'time': str(datetime.now())}
            eventlog.add_event_log('test', payload)
        eventlog.log_worker.wait()

if __name__ == '__main__':
    unittest.main()

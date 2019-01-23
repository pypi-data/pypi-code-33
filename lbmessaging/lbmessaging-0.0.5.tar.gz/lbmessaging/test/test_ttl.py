import json
import logging
import random
import sys
import unittest
import time

from lbmessaging.Common import Sender, Receiver
from lbmessaging.test import get_test_connection


class TestTTL(unittest.TestCase):

    def setUp(self):
        self._connection = get_test_connection()

    def tearDown(self):
        if self._connection:
            self._connection.close()

    def test_consumer(self):

        exchange = "test_exchange"
        queue = "test_queue_ttl"

        s = Sender(exchange, connection=self._connection)
        r = Receiver(exchange, queue, connection=self._connection)

        # Consume messages left over from previous runs
        r.receive_messages()

        mylist = range(5)

        # Sending some messages
        for i in mylist:
            # we should not see these
            s.send_message("test", json.dumps([i]), ttl=1)
        s.send_message('test', json.dumps(['ok']))
        time.sleep(6)
        m = r.receive_message()
        # Checking that we have the same number of messages and that
        # they are sorted correctly...
        self.assertEqual(json.loads(m[0]), ['ok'])


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

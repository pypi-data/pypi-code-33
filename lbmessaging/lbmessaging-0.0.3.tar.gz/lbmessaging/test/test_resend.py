import logging
import sys
import unittest

from lbmessaging.Common import Sender, Receiver
from lbmessaging.test import get_test_connection

class TestResend(unittest.TestCase):

    def setUp(self):
        self._connection = get_test_connection()

    def tearDown(self):
        if self._connection:
            self._connection.close()

    def test_resend(self):

        exchange = "test_exchange"
        queue = "test_queue"

        s = Sender(exchange, connection=self._connection)
        r = Receiver(exchange, queue, connection=self._connection)

        # Consume messages left over from previous runs
        r.receive_messages()

        # Sending a message
        s.send_message("test", "test_resend_body", max_retry=43)

        # Checking that we have the right message...
        msg = r.receive_message()
        self.assertEqual(msg.body, "test_resend_body")

        # Check that nothing else is in the queue
        msg2 = r.receive_message()
        self.assertEqual(None, msg2)

        # Resending
        s.resend_message(msg)

        # Check that we have the new message with a decreased retry count
        msg3 = r.receive_message()
        self.assertEqual(42, int(msg3.header_frame.headers['max_retry']))

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

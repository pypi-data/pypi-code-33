
import unittest
from check_certs.check_certs import Site

class TestSite(unittest.TestCase):
    def test_init(self):
        site = Site("www.google.com", {})

        self.assertEqual(site.port, 443)
        self.assertEqual(site.notify_when_expiring_in, 35)
        self.assertEqual(site.notifiers, [])

        site = Site("www.google.com", {
            "notify_when_expiring_in": 60,
        })
        self.assertEqual(site.notify_when_expiring_in, 60)

        # No tests for different ports for self.port yet because
        # ssl.create_connection(...) will try to make a connection to it
        # and it may fail if the port is not 443.

        # TODO:
        # mock ssl.create_connection(...) and test

    def test_register_notifier(self):

        site = Site("www.google.com", {})

        self.assertEqual(site.notifiers, [])

        notifier = object
        site.register_notifier(notifier)
        self.assertEqual(site.notifiers, [notifier])

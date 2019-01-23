from datetime import timedelta, datetime
from unittest import TestCase
from reliabilly.components.tools.date_utils import get_last_hour_epoch, get_current_epoch


class TestDateUtils(TestCase):

    def test_get_last_hour_epoch(self):
        response = get_last_hour_epoch()
        now = int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)
        self.assertEqual(now, response)

    def test_get_current_epoch_fail(self):
        response = get_current_epoch()
        now = int((datetime.now() + timedelta(seconds=2)).timestamp() * 1000)
        self.assertNotEqual(now, response)

    def test_get_last_hour_epoch_fail(self):
        now = get_last_hour_epoch()
        response = int((datetime.now() - timedelta(seconds=2)).timestamp() * 1000)
        self.assertNotEqual(now, response)

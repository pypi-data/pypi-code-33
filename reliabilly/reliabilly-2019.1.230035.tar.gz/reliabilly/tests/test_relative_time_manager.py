from unittest import TestCase
from dateutil import parser
from reliabilly.components.tools.relative_time_manager import RelativeTimeManager


class TestRelativeTimeManager(TestCase):

    def test_defaults(self):
        datetime = parser.parse("2018-05-29 07:48:23.175653")
        result = datetime - RelativeTimeManager.relative_delta()
        self.assertEqual(result.month, 4)

    def test_months(self):
        datetime = parser.parse("2018-05-29 07:48:23.175653")
        result = datetime - RelativeTimeManager.relative_delta("months")
        self.assertEqual(result.month, 4)

    def test_days(self):
        datetime = parser.parse("2018-05-29 07:48:23.175653")
        result = datetime - RelativeTimeManager.relative_delta("days")
        self.assertEqual(result.day, 28)

    def test_hours(self):
        datetime = parser.parse("2018-05-29 07:48:23.175653")
        result = datetime - RelativeTimeManager.relative_delta("hours")
        self.assertEqual(result.hour, 6)

    def test_minutes(self):
        datetime = parser.parse("2018-05-29 07:48:23.175653")
        result = datetime - RelativeTimeManager.relative_delta("minutes")
        self.assertEqual(result.minute, 47)

    def test_seconds(self):
        datetime = parser.parse("2018-05-29 07:48:23.175653")
        result = datetime - RelativeTimeManager.relative_delta("seconds")
        self.assertEqual(result.second, 22)

    def test_bad_period(self):
        datetime = parser.parse("2018-05-29 07:48:23.175653")
        result = datetime - RelativeTimeManager.relative_delta("blerch")
        self.assertEqual(result, datetime)

    def test_to_seconds(self):
        result = RelativeTimeManager.relative_delta_to_seconds("2018-05-29T22:35:10Z", "2018-06-05T04:50:24Z")
        self.assertEqual(result, 540914)

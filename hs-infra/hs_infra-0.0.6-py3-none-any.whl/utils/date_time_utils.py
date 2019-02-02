from datetime import timedelta

from dateutil import parser
from django.utils import timezone


class DateTimeUtils:
    @classmethod
    def get_current_datetime(cls):
        return timezone.now()

    @classmethod
    def get_datetime_by_delta(cls, days=None, seconds=None):
        """negative values for future datetime object."""
        timezone_now = timezone.now()
        if days or seconds:
            delta = timedelta(days=days, seconds=seconds)
            return timezone_now - delta
        return timezone_now

    @classmethod
    def convert_string_datetime_to_datetime(cls, string_datetime):
        return parser.parse(string_datetime)


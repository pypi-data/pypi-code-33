import arrow
import pytz
import random
import re

from arrow.arrow import Arrow
from dateutil import tz
from dateutil.relativedelta import relativedelta
from django.conf import settings
from math import ceil
from uuid import uuid4

safe_allowed_chars = "ABCDEFGHKMNPRTUVWXYZ2346789"


class MyTimezone:
    def __init__(self, timezone):
        if timezone:
            self.tzinfo = tz.gettz(timezone)
        else:
            self.tzinfo = tz.gettz(settings.TIME_ZONE)


class AgeValueError(Exception):
    pass


class ConvertError(Exception):
    pass


def get_uuid():
    return uuid4().hex


def round_up(value, digits):
    ceil(value * (10 ** digits)) / (10 ** digits)


def get_safe_random_string(length=12, safe=None, allowed_chars=None):
    safe = True if safe is None else safe
    allowed_chars = (
        allowed_chars
        or "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTUVWXYZ012346789!@#%^&*()?<>.,[]{}"
    )
    if safe:
        allowed_chars = "ABCDEFGHKMNPRTUVWXYZ2346789"
    return "".join([random.choice(allowed_chars) for _ in range(length)])


def convert_php_dateformat(php_format_string):
    php_to_python = {
        "A": "%p",
        "D": "%a",
        "F": "%B",
        "H": "%H",
        "M": "%b",
        "N": "%b",
        "W": "%W",
        "Y": "%Y",
        "d": "%d",
        "e": "%Z",
        "h": "%I",
        "i": "%M",
        "l": "%A",
        "m": "%m",
        "s": "%S",
        "w": "%w",
        "y": "%y",
        "z": "%j",
        "j": "%d",
        "P": "%I:%M %p",
    }
    python_format_string = php_format_string
    for php, py in php_to_python.items():
        python_format_string = python_format_string.replace(php, py)
    return python_format_string


def get_utcnow():
    return arrow.utcnow().datetime


def to_arrow_utc(dt, timezone=None):
    """Returns a datetime after converting date or datetime from
    the given timezone string to \'UTC\'.
    """
    try:
        dt.date()
    except AttributeError:
        # handle born as date. Use 0hr as time before converting to UTC
        tzinfo = MyTimezone(timezone).tzinfo
        r_utc = arrow.Arrow.fromdate(dt, tzinfo=tzinfo).to("utc")
    else:
        # handle born as datetime
        r_utc = arrow.Arrow.fromdatetime(dt, tzinfo=dt.tzinfo).to("utc")
    return r_utc


def get_dob(age_in_years, now=None):
    """Returns a DoB for the given age relative to now.

    Meant for tests.
    """
    if now:
        try:
            now = now.date()
        except AttributeError:
            pass
    now = now or get_utcnow().date()
    return now - relativedelta(years=age_in_years)


def age(born, reference_dt, timezone=None):
    """Returns a relative delta"""
    # avoid null dates/datetimes
    if not born:
        raise AgeValueError("Date of birth is required.")
    if not reference_dt:
        raise AgeValueError("Reference date is required.")
    # convert dates or datetimes to UTC datetimes
    born_utc = to_arrow_utc(born, timezone)
    reference_dt_utc = to_arrow_utc(reference_dt, timezone)
    rdelta = relativedelta(reference_dt_utc.datetime, born_utc.datetime)
    if born_utc.datetime > reference_dt_utc.datetime:
        raise AgeValueError(
            "Reference date {} {} precedes DOB {} {}. Got {}".format(
                reference_dt, str(reference_dt.tzinfo), born, timezone, rdelta
            )
        )
    return rdelta


def formatted_age(born, reference_dt=None, timezone=None):
    if born:
        tzinfo = MyTimezone(timezone).tzinfo
        born = arrow.Arrow.fromdate(born, tzinfo=tzinfo).datetime
        reference_dt = reference_dt or get_utcnow()
        age_delta = age(born, reference_dt or get_utcnow())
        if born > reference_dt:
            return "?"
        elif age_delta.years == 0 and age_delta.months <= 0:
            return "%sd" % (age_delta.days)
        elif age_delta.years == 0 and age_delta.months > 0 and age_delta.months <= 2:
            return "%sm%sd" % (age_delta.months, age_delta.days)
        elif age_delta.years == 0 and age_delta.months > 2:
            return "%sm" % (age_delta.months)
        elif age_delta.years == 1:
            m = age_delta.months + 12
            return "%sm" % (m)
        elif age_delta.years > 1:
            return "%sy" % (age_delta.years)
        else:
            raise TypeError(
                "Age template tag missed a case... today - born. "
                "rdelta = {} and {}".format(age_delta, born)
            )


def get_age_in_days(reference_datetime, dob):
    age_delta = age(dob, reference_datetime)
    return age_delta.days


def formatted_datetime(aware_datetime, php_dateformat=None, tz=None):
    """Returns a formatted datetime string, localized by default.
    """
    php_dateformat = php_dateformat or settings.SHORT_DATETIME_FORMAT
    tz = tz or pytz.timezone(settings.TIME_ZONE)
    utc = Arrow.fromdatetime(aware_datetime)
    local = utc.to(tz)
    return local.datetime.strftime(convert_php_dateformat(php_dateformat))


def to_utc(dt):
    """Returns UTC datetime from any aware datetime.
    """
    return Arrow.fromdatetime(dt, dt.tzinfo).to("utc").datetime


def convert_from_camel(name):
    """Converts from camel case to lowercase divided by underscores.
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

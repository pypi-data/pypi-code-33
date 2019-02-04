import uuid
from uuid import UUID

import pytz as pytz
from voluptuous import Invalid, Optional, Schema, All, Any, Required, Range

from shuttlis.pagination import after_to_offset


def valid_after(after: str) -> str:
    try:
        after_to_offset(after)
        return after
    except:
        raise Invalid("after")


def csv_strings(value):
    try:
        return [string for string in value.split(",")]
    except Exception as e:
        raise Invalid(str(e))


def military_time(time: int) -> int:
    hr, min = divmod(time, 100)
    if not (0 <= hr < 24 and 0 <= min < 60):
        raise Invalid("Invalid Military Time")
    return time


def timezone(tz):
    try:
        pytz.timezone(tz)
    except Exception as e:
        raise Invalid("Invalid timezone")


military_time_tz = Schema(
    {Required("time"): All(int, military_time), Required("timezone"): timezone}
)


location = Schema(
    {
        "lat": All(Any(float, int), Range(min=-90, max=90)),
        "lng": All(Any(float, int), Range(min=-180, max=180)),
    }
)


def int_validator(value: str) -> str:
    try:
        int(value)
        return value
    except Exception as e:
        raise Invalid(value)


pagination = Schema(
    {Optional("limit"): int_validator, Optional("after"): All(str, valid_after)}
)


def csv_uuids(string) -> [UUID]:
    return [uuid_validator(s) for s in string.split(",")]


def uuid_validator(value: str) -> str:
    try:
        uuid.UUID(value)
        return value
    except Exception as e:
        raise Invalid(value)

""" Serialize `Watch` object to and from JSON."""
# Standard modules
import copy
import datetime
import json


class DatetimeEncoder(json.JSONEncoder):
    """
    Serialize watch with json.
    """

    def default(self, o):  # pylint: disable=E0202
        """
        Method to serialize non-serializable oects. Serializes watch,
        timedelta and datetime.

        Args:
            o(: o: ): Object to serialize.
        """
        if isinstance(o, datetime.timedelta):
            return {
                'days': o.days,
                'seconds': o.seconds,
                'microseconds': o.microseconds
            }
        if isinstance(o, datetime.datetime):
            return {
                'year': o.year,
                'month': o.month,
                'day': o.day,
                'hour': o.hour,
                'minute': o.minute,
                'second': o.second,
                'microsecond': o.microsecond,
            }
        return json.JSONEncoder.default(self, o)


def deserialize(attributes):
    """
    Deserialize watch attributes.

    Args:
        attributes(dict): Serialized watch attributes.

    Returns:
        (dict): Deserialized watch attributes
    """
    try:
        # Don't touch the original
        attributes = copy.deepcopy(attributes)

        # Deserialize interval
        interval = attributes.pop('interval')
        attributes['interval'] = datetime.timedelta(**interval)

        # Deserialize date
        date = attributes.pop('date')
        attributes['date'] = datetime.datetime(**date)
    except AttributeError:
        return None

    return attributes

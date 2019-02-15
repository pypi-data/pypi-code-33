from datetime import datetime, date, timedelta
from jsonpickle.handlers import BaseHandler


class MongoDatetimeHandler(BaseHandler):
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fffZ'
    """
    Custom handler for datetime objects
    """
    MICROSECONDS_KEY = 'microsecond'

    def flatten(self, obj, data):
        pickler = self.context
        if not pickler.unpicklable:
            return obj
        data['inner_date'] = obj
        if isinstance(obj, datetime):
            data['microsecond'] = obj.microsecond
        return data

    def restore(self, data):
        original_datetime = data['inner_date']
        if 'microsecond' in data:
            original_datetime += timedelta(microseconds=data['microsecond']
                                                        - data['inner_date'].microsecond)
        return original_datetime


class MongoDateHandler(BaseHandler):
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fffZ'
    """
    Custom handler for date objects
    """

    def flatten(self, obj, data):
        pickler = self.context
        if not pickler.unpicklable:
            return obj

        date_as_dt = datetime(obj.year,
                              obj.month,
                              obj.day)
        data['inner_date'] = date_as_dt
        return data

    def restore(self, data):
        original_datetime = data['inner_date']
        return original_datetime.date()

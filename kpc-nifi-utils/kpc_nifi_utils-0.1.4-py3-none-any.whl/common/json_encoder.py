import datetime
import decimal
import json


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return obj.seconds
        elif isinstance(obj, decimal.Decimal):
            return float(str(obj))
        else:
            return super().default(obj)

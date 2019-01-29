import ast
import json

from infi.clickhouse_orm import fields
from infi.clickhouse_orm.utils import escape
from six import text_type, string_types, binary_type


class BoolField(fields.Field):
    class_default = False
    db_type = 'UInt8'

    def to_python(self, value, timezone_in_use):
        if isinstance(value, string_types):
            value = value.lower()
        if value in (1, '1', True, 'true'):
            return True
        elif value in (0, '0', False, 'false'):
            return False
        else:
            raise ValueError('Invalid value for %s - %r' % (self.__class__.__name__, value))

    def to_db_string(self, value, quote=True):
        return text_type(self.to_kafka(value))

    def to_kafka(self, value):
        return int(value)


class BoolStringField(BoolField):
    class_default = False
    db_type = 'String'

    def to_kafka(self, value):
        return str(value).lower()


class DateField(fields.DateField):
    def to_kafka(self, value):
        return self.to_db_string(value, quote=False)


class DateTimeField(fields.DateTimeField):
    def to_kafka(self, value):
        return self.to_db_string(value, quote=False)


class JsonStringField(fields.StringField):
    class_default = {}

    def to_python(self, value, timezone_in_use):
        if isinstance(value, string_types):
            return json.loads(value)
        elif isinstance(value, (dict, list)):
            return value
        else:
            raise ValueError('Invalid value for %s - %r' % (self.__class__.__name__, value))

    def to_db_string(self, value, quote=True):
        return escape(self.to_kafka(value), quote)

    def to_kafka(self, value):
        return json.dumps(value)


class ListStringField(fields.StringField):
    class_default = []

    def to_python(self, value, timezone_in_use):
        if isinstance(value, string_types):
            return ast.literal_eval(value)
        if isinstance(value, list):
            return value
        else:
            raise ValueError('Invalid value for %s - %r' % (self.__class__.__name__, value))

    def to_kafka(self, value):
        return self.to_db_string(value, quote=False)


class StringField(fields.StringField):
    def to_python(self, value, timezone_in_use):
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, text_type):
            return value
        if isinstance(value, binary_type):
            return value.decode('UTF-8')
        raise ValueError('Invalid value for %s: %r' % (self.__class__.__name__, value))
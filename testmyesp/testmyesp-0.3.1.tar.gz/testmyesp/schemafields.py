
import base64

from colibris.schemas import ValidationError
from colibris.schemas import fields


class Base64Field(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ''

        return base64.b64encode(value).decode()

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return base64.b64decode(value)

        except Exception as e:
            raise ValidationError('Invalid base-64 value: {}.'.format(e))

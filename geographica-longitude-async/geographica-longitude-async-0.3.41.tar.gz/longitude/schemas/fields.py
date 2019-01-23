from marshmallow import ValidationError
from marshmallow.fields import *
from geojson import Point


class GeojsonPoint(Dict):

    def _deserialize(self, value, attr, data):
        value = super()._deserialize(value, attr, data)

        try:
            value = Point.to_instance(value)
        except (TypeError, AttributeError, ValueError, UnicodeDecodeError) as e:
            raise ValidationError(e.message)

        return value

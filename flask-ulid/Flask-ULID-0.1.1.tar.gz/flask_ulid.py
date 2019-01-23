from werkzeug.routing import BaseConverter, ValidationError
from ulid import from_str

__version__ = '0.1.1'


class ULIDConverter(BaseConverter):
    """
    ULID converter for the Werkzeug routing system.
    """

    def __init__(self, map):
        super(ULIDConverter, self).__init__(map)

    def to_python(self, value):
        s = str(value)
        if len(s) != 26:
            raise ValidationError()

        try:
            return from_str(s)
        except ValueError:
            raise ValidationError()

    def to_url(self, value):
        return str(value)


class FlaskULID(object):
    """Flask extension providing a ULID url converter"""

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.url_map.converters['ulid'] = ULIDConverter

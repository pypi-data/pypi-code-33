from werkzeug.routing import BaseConverter


class HexConverter(BaseConverter):
    "Validate hexadecimal numbers"

    regex = r'[0-9a-fA-F]+'

    def to_python(self, value):
        return value

    def to_url(self, value):
        if isinstance(value, int):
            return hex(value)[2:]
        return value


converters = {
    'hex': HexConverter,
}

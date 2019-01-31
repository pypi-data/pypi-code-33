""" Module that monkey-patches json module when it's imported so
JSONEncoder.default() automatically checks for a special "toJSON()"
method and uses it to encode the object if found.
"""
from json import JSONEncoder

def _default(self, obj):
    return getattr(obj.__class__, "toJSON", _default.default)(obj)

_default.default = JSONEncoder().default  # Save unmodified default.
JSONEncoder.default = _default # Replace it.
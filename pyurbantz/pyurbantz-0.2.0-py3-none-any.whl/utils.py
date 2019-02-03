from urbantz.base import JSONSerializable
import re


def to_camel_case(value):
    return re.sub(r'_(.)', lambda m: m.group(1).upper(), value)


class DictObject(JSONSerializable, dict):
    """
    A utility class that turns a dict's items into object attributes.
    This also performs snake to camel case conversion:
    if a key is missing in the original dict, the key gets converted
    to camel case.

    >>> d = DictObject(first_name='Chuck', lastName='Norris')
    >>> d.first_name
    'Chuck'
    >>> d.last_name
    'Norris'
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__.update(self)

    def toJSON(self):
        return dict(self)

    @classmethod
    def fromJSON(cls, payload):
        return cls(payload)

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            return super().__getattr__(name)

    def __missing__(self, name):
        camel = to_camel_case(name)
        if name == camel:  # Prevent recursion
            raise KeyError(name)
        return self.__getitem__(camel)

    def __delattr__(self, name):
        if name in self:
            try:
                self.__delitem__(name)
                return
            except KeyError:
                pass
        super().__delattr__(self, name)

    def __delitem__(self, name):
        try:
            super().__delitem__(name)
        except KeyError:
            camel = to_camel_case(name)
            if name == camel:
                raise
            super().__delitem__(camel)

    def __contains__(self, name):
        return super().__contains__(name) \
            or super().__contains__(to_camel_case(name))

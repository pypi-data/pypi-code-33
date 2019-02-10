
class Struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._attributes = kwargs

    def __repr__(self):
        return '<{CLASSNAME} {ATTRIBS!s}>'.format(
            CLASSNAME = self.__class__.__name__,
            ATTRIBS   = self._attributes
        )

    def __eq__(self, other):
        try:
            return self._attributes == other._attributes
        except AttributeError:
            return False

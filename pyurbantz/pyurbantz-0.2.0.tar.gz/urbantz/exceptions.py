from urbantz.base import JSONSerializable


class APIError(JSONSerializable, Exception):
    """
    An error returned by the UrbanTZ API.
    This does not include HTTP errors.
    """

    def __init__(self, error):
        """
        :param error: Parsed JSON error from the API.
        :type error: dict
        """
        self.message = error.get('message')
        self.code = error.get('code')

    def __repr__(self):
        return "<APIError {}>".format(repr(str(self)))

    def __str__(self):
        return self.message or 'Unknown error'

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            self.code == other.code and self.message == other.message

    @classmethod
    def fromJSON(cls, payload):
        return cls(payload)

    def toJSON(self):
        return {'message': self.message, 'code': self.code}

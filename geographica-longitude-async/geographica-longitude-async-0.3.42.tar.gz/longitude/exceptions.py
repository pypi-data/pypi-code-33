from sanic.exceptions import *
from sanic_jwt.exceptions import *
from marshmallow.exceptions import *


class InvalidAttribute(InvalidUsage):

    attr_name = None

    def __init__(self, attr_name, message=None, status_code=None):

        if message is None:
            message = 'Value "{}" is invalid or missing.'

        self.attr_name = attr_name

        super().__init__(
            message.format(attr_name),
            status_code=status_code
        )

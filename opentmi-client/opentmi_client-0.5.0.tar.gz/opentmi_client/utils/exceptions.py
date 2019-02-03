"""
OpenTMI client exceptions
"""


class OpentmiException(Exception):
    """
    Default Opentmi Exception
    """
    def __init__(self, message):
        """
        Constructor
        :param message:
        """
        Exception.__init__(self, message)
        self.message = message


class TransportException(OpentmiException):
    """
    Transport exception
    """
    def __init__(self, message, code=None):
        """
        Constructor for Transport exceptions
        :param message: string
        :param code: status_code or None
        """
        OpentmiException.__init__(self, message)
        self.code = code

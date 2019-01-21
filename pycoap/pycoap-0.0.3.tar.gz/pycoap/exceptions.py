
class CoapException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "<{} Error:  {}>".format(self.__class__.__name__, self.message)


class NameResolutionError(CoapException):
    pass

class InvalidRequest(CoapException):
    pass

class MessageTimeoutError(CoapException):
    pass

class ProtocolError(CoapException):
    pass

class ReceiveTimeoutError(CoapException):
    pass

class TokenMismatchError(CoapException):
    pass

class NotObservableError(CoapException):
    pass

class Block1Error(CoapException):
    pass

class Block2Error(CoapException):
    pass
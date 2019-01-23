





class MTException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "{} Error:  {}".format(self.__class__.__name__, self.message)
       
class CoapRequestTimedOut(MTException):
    pass

class ConnectionRefused(MTException):
    pass

class NoRouteToHost(MTException):
    pass

class NameNotResolved(MTException):
    pass

class ResponseError(MTException):
    pass

class DeviceNotFound(MTException):
    pass

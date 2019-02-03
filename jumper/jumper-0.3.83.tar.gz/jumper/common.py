class VlabException(Exception):
    def __init__(self, message, exit_code):
        super(VlabException, self).__init__(message)
        self.exit_code = exit_code
        self.message = message


class EmulationError(VlabException):
    def __init__(self, message):
        super(EmulationError, self).__init__(message, 5)


class MissingFileError(VlabException):
    def __init__(self, message):
        super(MissingFileError, self).__init__(message, 2)


class ArgumentError(VlabException):
    def __init__(self, message):
        super(ArgumentError, self).__init__(message, 1)

class TimeoutException(VlabException):
    def __init__(self, message="Timeout decorator exception"):
        super(TimeoutException, self).__init__(message, 9)


class JemuConnectionException(VlabException):
    def __init__(self, message="Connection failed"):
        super(JemuConnectionException, self).__init__(message, 8)


class WrongStateError(VlabException):
    def __init__(self, message=""):
        super(WrongStateError, self).__init__(message, 10)


class VlabEnvironmentError(VlabException):
    def __init__(self, message=""):
        super(VlabEnvironmentError, self).__init__(message, 11)

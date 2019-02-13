class HLSFileException(Exception):
    def __init__(self, message=None):
        super(Exception, self).__init__(message)
        if message is not None:
            self.message = message


class FileException(HLSFileException):
    def __init__(self, message):
        super(HLSFileException, self).__init__(message)


class MissingArguments(HLSFileException):
    def __init__(self, message):
        super(HLSFileException, self).__init__(message)

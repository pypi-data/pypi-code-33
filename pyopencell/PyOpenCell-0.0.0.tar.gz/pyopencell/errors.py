class PyOpenCellError(Exception):
    def __init__(self, message):
        super(PyOpenCellError, self).__init__(message)
        self.message = message


class ArgumentMissingError(PyOpenCellError):
    pass


class HTTPError(PyOpenCellError):
    pass

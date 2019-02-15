# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Package-specific exception hierarchy."""


__all__ = ['codify', 'CodedException', 'CodedValueError', 'CodedTypeError',
           'InvalidPlanarShape']


def codify(ExceptionClass):
    """Decorate exception classes so that
    they are associated to an error-code,
    accessible through a ``code`` class-attribute.
    """
    class CodedException(ExceptionClass):
        """ The decorated exception class.

        :param code: The code of the exception.
        :type code: str or int
        :param str emsg: The error message.
        """
        def __init__(self, code, emsg):
            self.code = str(code)
            super().__init__(emsg)

    return CodedException


CodedException = codify(Exception)
CodedValueError = codify(ValueError)
CodedTypeError = codify(TypeError)


@codify
class InvalidPlanarShape(ValueError):
    """Raise when a user-defined planar shape
    is invalid
    """
    pass

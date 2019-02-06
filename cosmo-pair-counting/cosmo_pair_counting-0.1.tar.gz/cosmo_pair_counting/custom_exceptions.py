"""
Classes for all LSS_Utils-specific exceptions
"""

__all__ = ["LSSUtils_Error"]

class LSSUtils_Error(Exception):
    """Base class of all LSS_Utils-specific exceptions"""
    def __init__(self, message):
        super(LSSUtils_Error, self).__init__(message)

"""
Classes for all SDSS_Catl_utils-specific exceptions
"""

__all__ = ["SDSSCatlUtils_Error"]

class SDSSCatlUtils_Error(Exception):
    """Base class of all LSS_Utils-specific exceptions"""
    def __init__(self, message):
        super(SDSSCatlUtils_Error, self).__init__(message)

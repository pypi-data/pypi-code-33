
class SkyError(Exception):
    """Base class from which all Exceptions on Sky derive. Useful for catching all errors regardless of type and case."""
    pass

########################################################################################################################
#
# Sky Developer Errors
#
#########################################################################################################################

class SkySDKError(Exception):
    """Raise if errors occur through functionality used during app development."""
    pass

class SkySDKRequestParserError(SkySDKError):
    """Raise if an AetherApplication Request Parser fails for any reason."""
    pass

class SkySDKRuntimeError(SkySDKError):
    """Raise if an AetherApplication fails during the execution of the run() method."""
    pass


########################################################################################################################
#
# Sky User Errors
#
#########################################################################################################################

class SkyValueError(SkyError, ValueError):
    """Raised if parameters passed into Sky are invalid or referred to an object or data that does not exist."""
    pass

class SkyTypeError(SkyError, ValueError):
    """Raised if parameters passed into Sky referred to a type object or attribute name that does not exist."""
    pass

class SkyRuntimeError(SkyError, RuntimeError):
    """Raised if Sky operation fails due to invalid state or server side error."""
    pass

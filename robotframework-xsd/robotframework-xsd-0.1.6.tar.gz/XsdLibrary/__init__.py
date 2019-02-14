from .xsd import XsdKeywords
from .version import VERSION

_version_ = VERSION


class XsdLibrary(XsdKeywords):
    """
    XsdLibrary is a XSD keyword library that uses to validate XML
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

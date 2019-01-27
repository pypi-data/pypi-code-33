from enum import Enum


class ColumnType(Enum):
    """ Enumeration class for all possible DB types with which this library can
    deal.
    
    .. note:: See the source code for helper methods that each enumeration has.
    """
    
    # for Python versions prior to 3.6
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj
    
    # binary
    BINARY = ()         #: Any type of binary data
    
    # boolean
    BOOLEAN = ()        #: Boolean value
    
    # strings
    STRING = ()         #: String value, like *char* or *varchar*
    TEXT = ()           #: String unlimited in length
    
    # numbers
    INTEGER = ()        #: Any type of integer data
    FLOAT = ()          #: Any type of number values with fraction
    
    # dates and times
    DATE = ()           #: Date value
    TIME = ()           #: Time value
    DATETIME = ()       #: Date and time value (*timestamp*)
    
    # unknown
    OTHER = ()          #: Unknown data type
    
    
    def is_num(self):
        return self in (ColumnType.INTEGER, ColumnType.FLOAT)
    
    def is_str(self):
        return self in (ColumnType.STRING, ColumnType.TEXT)
    
    

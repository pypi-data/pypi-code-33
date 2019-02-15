from enum import Enum


class RelationType(Enum):
    """ Enumeration class for all possible relation types.
    
    .. note:: See the source code for helper methods that each enumeration has.
    """
    
    # for Python versions prior to 3.6
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj
    
    ONE_TO_ONE = ()
    ONE_TO_MANY = ()
    MANY_TO_ONE = ()
    MANY_TO_MANY = ()
    
    
    def is_x_to_one(self):
        return self in (RelationType.ONE_TO_ONE, RelationType.MANY_TO_ONE)
    
    def is_x_to_many(self):
        return self in (RelationType.ONE_TO_MANY, RelationType.MANY_TO_MANY)
    
    def is_one_to_x(self):
        return self in (RelationType.ONE_TO_ONE, RelationType.ONE_TO_MANY)
    
    def is_many_to_x(self):
        return self in (RelationType.MANY_TO_ONE, RelationType.MANY_TO_MANY)
from enum import Enum

class ComputeJobType(Enum):
    """
    Enum for different compute job types. This is used both by the
    classes that schedule compute jobs as well as the ComputeStrategyMixin
    and ComputeBase classes.
    """
    Fit = 1    
    CVSearch = 2,
    ForecasterUnion = 3,
    Custom = 4
    

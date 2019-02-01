# system modules

# internal modules
from class_tools.decorators import *

# external modules


@with_init_from_properties()
@with_eq_comparing_properties()
@with_repr_like_init_from_properties()
class PropertyObject:
    """
    Convenience base class decorated with :any:`with_init_from_properties`,
    :any:`with_eq_comparing_properties` and
    :any:`with_repr_like_init_from_properties`.
    """

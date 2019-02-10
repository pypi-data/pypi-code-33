try:
    import bge
    is_component_step = hasattr(bge, '__component__')
    PythonComponent = bge.types.KX_PythonComponent

except ImportError:
    is_component_step = False
    PythonComponent = object

from .launcher import *

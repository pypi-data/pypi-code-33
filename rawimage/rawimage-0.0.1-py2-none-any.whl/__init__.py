__version__ = '0.0.1'

try:
    from rawimage.rawimage import *
except ImportError:
    from rawimage import *
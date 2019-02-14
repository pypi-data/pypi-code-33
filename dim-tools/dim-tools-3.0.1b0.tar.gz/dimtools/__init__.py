try:
    from .cls_readconf import ReadConfig
except ImportError:
    from cls_readconf import ReadConfig

try:
    from .fnc_mkdir import main as makedir
except ImportError:
    from fnc_mkdir import main as makedir

try:
    from .fnc_readargs import main as readargs
except ImportError:
    from fnc_readargs import main as readargs

try:
    from .fnc_walker import main as walker
except ImportError:
    from fnc_walker import main as walker

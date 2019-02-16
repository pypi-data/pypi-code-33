from .__meta__ import __version__

from .chart import Chart

# from .util import Util

# get_license = Util.get_license

def _jupyter_nbextension_paths():
    return [{
        # fixed syntax
        'section': 'notebook',
        # path relative to module directory - here: ipyhc
        'src': 'static',
        # directory in the `nbextension/` namespace
        'dest': 'ipyhc',
        # path in the `nbextension/` namespace
        'require': 'ipyhc/extension'
    }]

import sys
if sys.version_info.major>=3:
    from .beaucage import *
else:
    from beaucage import *

import sys

from .auto_reverse import *
from .constraints import *
from .fields import *
from .general import *
from .many_refs import *


if 'manage.py' not in sys.argv and './manage.py' not in sys.argv:
    # Django will not allow to create migrations for the models
    from .invalid_fields import *
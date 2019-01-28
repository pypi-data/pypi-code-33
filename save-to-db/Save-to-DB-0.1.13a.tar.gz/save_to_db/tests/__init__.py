from . import test_adapters
from .test_core import *
from .test_core_utils import *

# loading all adapter tests into current name space
test_adapters.init()
for registered_test in test_adapters.registered_tests:
    globals()[registered_test.__name__] = registered_test
registered_test = None  # removing reference in order not to load with `inspect`
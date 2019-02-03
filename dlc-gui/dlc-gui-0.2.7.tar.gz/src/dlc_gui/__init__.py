__version__ = "0.2.7"

import sys

if hasattr(sys, "_called_from_test"):
    print("In pytest, skipping __init__.py")
else:
    from .gui import show

    __all__ = ["show"]

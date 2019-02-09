import sys

if hasattr(sys, "_called_from_test"):
    print("In pytest, skipping __init__.py")
else:
    from .gui import show  # pragma: no cover

    __all__ = ["show"]  # pragma: no cover

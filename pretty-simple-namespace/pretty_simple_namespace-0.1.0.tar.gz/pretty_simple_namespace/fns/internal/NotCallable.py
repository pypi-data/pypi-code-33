from types import SimpleNamespace
from .mAssignToSelf import mAssignToSelf
from .raise_ import raise_
import os


class NotCallable(SimpleNamespace):
    def __init__(self, fnName, **typeToFn):
        self._fnName = fnName
        self._typeToFn = typeToFn
        mAssignToSelf(typeToFn, self)

    def __call__(self, *args, **kwargs):
        availableKeys = list(self._typeToFn.keys())
        fnName = self._fnName

        raise_(
            TypeError,
            f"""
            The utility '{fnName}' is not callable because it needs to know what
            to return in the case of an empty list.

            example usage:
            {fnName}.{availableKeys[0]}([...])

            available keys:
              {os.linesep.join(availableKeys)}
            """,
        )

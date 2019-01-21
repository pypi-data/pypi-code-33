from inspect import signature
from ..internal.raise_ import raise_
import wrapt


def argIsInstance(aType, fnName=None):
    @wrapt.decorator
    def wrapper(fn, _instance, args, kwargs):
        nonlocal fnName

        typePassed = type(args[0])
        if not isinstance(typePassed, aType):
            argName = list(signature(fn).parameters)[0]
            fnName = fnName or fn.__name__
            typeName = aType.__name__
            raise_(
                ValueError,
                f"""
                {fnName} requires {argName} to be an instance of {typeName}
                type passed: {typePassed.__name__}
                """,
            )

        return fn(*args, **kwargs)

    return wrapper

from types import *


__all__ = [ 'pluckit' ]


def pluckit(obj, handle):
    if obj is None or handle is None:
        # None has nothing to pluck...
        return obj

    # function pointer
    if callable(handle):
        return handle(obj)

    # dict-like key
    if hasattr(obj, 'keys'):
        return obj[handle]

    # object attribute or class method
    if type(handle) == str and hasattr(obj, handle):
        attr = getattr(obj, handle)

        # make sure it's a class method, not a legit returned callable
        if isinstance(attr, (
            BuiltinFunctionType, BuiltinMethodType,
            FunctionType, MethodType,
        )):
            # use method's return value
            return attr()

        # class attribute
        return attr

    # list-like index
    if hasattr(obj, '__getitem__') and isinstance(handle, int):
        return obj[handle]

    raise TypeError('invalid handle: %s' % handle)

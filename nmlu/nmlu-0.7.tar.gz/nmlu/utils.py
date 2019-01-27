import types


def noglobals(f):
    return types.FunctionType(f.__code__, {})

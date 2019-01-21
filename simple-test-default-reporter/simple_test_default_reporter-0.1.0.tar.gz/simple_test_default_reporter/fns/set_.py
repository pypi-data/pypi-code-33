from copy import copy


def set_(name, value):
    def set_inner(obj):
        result = copy(obj)
        setattr(result, name, value)
        return result

    return set_inner

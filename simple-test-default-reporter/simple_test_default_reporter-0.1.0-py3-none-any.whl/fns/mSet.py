def mSet(name, value):
    def mSet_inner(obj):
        setattr(obj, name, value)
        return obj

    return mSet_inner

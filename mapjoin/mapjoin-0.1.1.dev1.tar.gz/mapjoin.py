def mapjoin(*args, sep=None, key=None):
    return (sep or ' ').join(map(key or str, args))

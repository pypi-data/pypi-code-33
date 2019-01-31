def mapjoin(*args, sep=None, key=None):
    return (sep or ' ').join(map(key, args) if key else args)


def strjoin(*args, sep=None):
    return mapjoin(*args, sep=sep, key=str)

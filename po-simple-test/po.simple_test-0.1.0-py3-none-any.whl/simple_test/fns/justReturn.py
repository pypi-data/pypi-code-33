def justReturn(something):
    return lambda *args, **kwargs: something

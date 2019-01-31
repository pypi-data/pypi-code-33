def cpd(f):
    """
    cpd - cached property decorator
    "caches" the result of an actual property function
    """
    @property
    def wrapper(self, *args, **kwargs):
        value = getattr(self, f'_{f.__name__}', None)
        if value is None:
            value = f(self, *args, **kwargs)
            setattr(self, f'_{f.__name__}', value)
        return value
    return wrapper

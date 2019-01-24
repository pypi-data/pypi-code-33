class cached_property(object):
    '''
    Computes attribute value and caches it
    http://stackoverflow.com/questions/3237678
    Author: Denis Otkidach
    '''
    def __init__(self, method, name=None):
        self.method = method
        self.name = name or method.__name__
        self.__doc__ = method.__doc__

    def __get__(self, inst, cls):
        if inst is None:
            return self
        elif self.name in inst.__dict__:
            return inst.__dict__[self.name]
        else:
            result = self.method(inst)
            inst.__dict__[self.name] = result
            return result

    def __set__(self, inst, value):
        raise AttributeError("This property is read-only")

    def __delete__(self, inst):
        del inst.__dict__[self.name]

import structured_config


class _ConstructionOrderDict(dict):
    """Track field order and ensure field names are not reused.

    TypeStructure will use the names found in self.__field_names__ to translate
    to indices.
    """

    def __init__(self, *args, **kwds):
        self.__field_names__ = []
        super(_ConstructionOrderDict, self).__init__(*args, **kwds)

    def __setitem__(self, key, value):
        """Records anything not dundered or not a descriptor.

        If a field name is used twice, an error is raised.

        Single underscore (sunder) names are reserved.
        """
        if key in self.__field_names__:
            # overwriting a field?
            raise TypeError('Attempted to reuse field name: %r' % key)
        elif key[:2] == key[-2:] == '__':
            pass
        elif not (hasattr(value, '__get__') or  # Check not a descriptor
                  hasattr(value, '__set__') or
                  hasattr(value, '__delete__')):
            self.__field_names__.append(key)
        super(_ConstructionOrderDict, self).__setitem__(key, value)


import collections

class TypeStructure(type):

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return collections.OrderedDict()

    def __new__(cls, name, bases, namespace, **kwds):
        result = type.__new__(cls, name, bases, dict(namespace))
        result.__field_names__ = [n for n in namespace if not(n[:2] == n[-2:] == '__')]
        for base in bases:
            if base is not structured_config.Structure and \
                    issubclass(base, structured_config.Structure):
                result.__field_names__.extend(base().__field_names__)
        return result

    def __iter__(cls):
        return iter([(k, getattr(cls, k)) for k in cls.__field_names__ if k[0] != '_'])


# class TypeStructure(type):
#     @classmethod
#     def __prepare__(mcs, cls, bases, *args, **kwargs):
#         return _ConstructionOrderDict()
#
#     def __init__(cls, name, bases, dct):
#         cls.__field_names__ = dct.__field_names__
#         super(TypeStructure, cls).__init__(name, bases, dct)
#
#     def __iter__(cls):
#         return iter([(k, getattr(cls, k)) for k in cls.__field_names__ if k[0] != '_'])

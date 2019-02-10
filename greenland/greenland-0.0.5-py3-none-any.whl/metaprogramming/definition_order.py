
import collections

class WithDefinitionOrderMeta(type):

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return collections.OrderedDict()

    def __new__(cls, name, bases, namespace, **kwds):
        Class = type.__new__(cls, name, bases, dict(namespace))
        Class.__members_definition_order__ = tuple((key for key in namespace.keys() if key[0]!='_'))
        return Class

class WithDefinitionOrder( object, metaclass = WithDefinitionOrderMeta ): pass

import weakref

__all__ = [
    'Symbol', 'getid',
]

def getid(
    thing: object,
    module: str = None,
    qualname: str = None,
    name: str = None,
) -> str:
    '''Returns some kind of id for `thing`\n
    :param thing: object to get the id for\n
    :param module: str fallback\n
    :param qualname: str fallback\n
    :param name: str fallback\
    '''
    parts = []
    module = getattr(thing, '__module__', module)
    name = getattr(thing, '__qualname__', None) \
        or getattr(thing, '__name__', name)
    if module: parts.append(module)
    if name: parts.append(name)
    return '.'.join(parts)

class Symbol:
    '''Unique symbol, despite the use of the same target.'''
    __slots__ = [
        'name'
    ]

    REGISTRY = {}

    id = property(id)

    def __init__(self, target: object = None):
        try:
            self.name = str(target)
        except ValueError:
            self.name = getid(target)

    def __str__(self):
        return self.name

    def __bool__(self):
        return True

    @classmethod
    def For(cls, target):
        return cls.REGISTRY.get(target, False) \
            or cls.REGISTRY.setdefault(target, cls(target))

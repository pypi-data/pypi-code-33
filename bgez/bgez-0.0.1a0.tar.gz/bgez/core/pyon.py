from typing import Any

from bgez.core.utils.symbol import Symbol

__all__ = [
    'Pyon',
]

class Pyon(dict):
    '''\
    This object behaves like JSON (JavaScript Object Notation),
    where you can access the dict items with the dot notation.
    '''

    # Symbols to avoid key collisions
    MISSING = Symbol('__missing__')
    DEFAULT = Symbol('__default__')

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        def missing(self, attribute):
            return self.__getitem__(type(self).DEFAULT)
        self.__setitem__(type(self).MISSING, missing)

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __missing__(self, attribute: str) -> Any:
        try: return self.__getitem__(type(self).MISSING)(self, attribute)
        except KeyError as e:
            raise KeyError(attribute)

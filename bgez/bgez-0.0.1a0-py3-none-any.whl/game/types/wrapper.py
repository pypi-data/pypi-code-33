from typing import Generic, TypeVar, Optional, MutableMapping, Iterator, Dict, Type

from weakref import WeakKeyDictionary

from bgez.core import logger, undefined

from bge.types import EXP_PyObjectPlus, EXP_ListValue

__all__ = [
    'PyObjectPlus',
    'register_wrapper', 'wrap',
    'ListValue',
]

__wrapped__: MutableMapping[object, 'PyObjectPlus'] = WeakKeyDictionary()
__wrapper__: Dict[Type[EXP_PyObjectPlus], 'Type[PyObjectPlus]'] = {}

class PyObjectPlus:
    '''
    Wraps Blender Game Engine's PyObjectPlus instances.
    They basically act as dict-like object, storing "game properties".
    '''

    def __init__(self, pyobject: EXP_PyObjectPlus):
        self._pyobject = pyobject

    def __bool__(self):
        return not self.invalid

    @property
    def invalid(self) -> bool:
        return self._pyobject.invalid

def register_wrapper(bge_type: Type):
    '''
    Decorate a `PyObjectPlus` subclass to wrap a specific bge type.
    '''
    def class_decorator(cls):
        __wrapper__[bge_type] = cls
        return cls
    return class_decorator

def wrap(object: Optional[EXP_PyObjectPlus]):
    '''
    Wrap as many BGE types as possible.
    '''
    if object is None:
        return None

    if isinstance(object, PyObjectPlus):
        return object

    wrapped = __wrapped__.get(object, None)
    if wrapped is not None:
        return wrapped

    cls = object.__class__
    for base in cls.__mro__:
        if base in __wrapper__:
            wrapped = __wrapper__[base](object)
            __wrapped__[object] = wrapped
            return wrapped

    logger.warning(f'cannot wrap type: {type(object)}')
    return object

T = TypeVar('T', bound=PyObjectPlus)
@register_wrapper(EXP_ListValue)
class ListValue(PyObjectPlus, Generic[T]):
    '''
    Because BGEz provides its own wrappers, we also wrap EXP_ListValue, so
    when we access an object inside the list, we get the right type.
    '''

    def __str__(self):
        elements = ', '.join(str(object) for object in self)
        return f'{self.__class__.__qualname__}[{elements}]'

    def __iter__(self) -> Iterator[T]:
        for object in self._pyobject:
            yield wrap(object)

    def __getitem__(self, key) -> T:
        return wrap(self._pyobject.__getitem__(key))

    def __delitem__(self, key) -> None:
        self._pyobject.__delitem__(key)

    def get(self, key, default = undefined) -> T:
        if default is undefined:
            return wrap(self._pyobject.get(key))
        return wrap(self._pyobject.get(key, default))

    def append(self, element) -> None:
        self._pyobject.append(element)

    def index(self, element) -> int:
        return self._pyobject.index(element)

    def reverse(self) -> None:
        self._pyobject.reverse()

    def filter(self, name: str, property: str) -> 'ListValue[T]':
        return wrap(self._pyobject.find(name, property))

    def from_id(self, id: int) -> T:
        return wrap(self._pyobject.from_id(id))

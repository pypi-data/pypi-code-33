'''Dict serialization methods.'''
from typing import (
    Any,
    Callable,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    TypeVar,
)
from base64 import (b64encode)
from datetime import (date as Date, datetime as DateTime)
from decimal import (Decimal)
from uuid import (UUID)

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')
Record = Mapping[str, Any]
Bytes = bytes

class Serialize:
  '''Contains serialization methods. They're placed as static methods on a class to avoid
  name conflicts.
  '''
  @staticmethod
  def map(fn: Callable[[T], U]) -> Callable[[Iterable[T]], List[U]]:
    '''Returns a function that accepts a iterable and maps over it with fn.'''
    def mapper(items: Iterable[T]) -> List[U]:
      return [fn(item) for item in items]
    return mapper

  @staticmethod
  def pick(keys: Sequence[str]) -> Callable[[Record], Record]:
    '''Returns a new mapping with only the keys specified.'''
    def picker(item: Record) -> Record:
      return {k: item[k] for k in keys if k in item}
    return picker

  @staticmethod
  def exclude(keys: Set[str]) -> Callable[[Record], Record]:
    '''Returns a new mapping without the keys specified.'''
    def excluder(item: Record) -> Record:
      return {k: v for (k, v) in item.items() if k not in keys}
    return excluder

  @staticmethod
  def evolve(maps: Mapping[str, Callable[[Any], Any]]) -> Callable[[Record], Record]:
    '''Returns a new mapping with certain keys mapped as specified.'''
    def evolver(item: Record) -> Record:
      return {k: (maps[k](v) if k in maps else v) for (k, v) in item.items()}
    return evolver

  @staticmethod
  def compose(outer: Callable[[U], V], inner: Callable[[T], U]) -> Callable[[T], V]:
    '''Returns a single function that composes outer of inner.'''
    def composer(val: T) -> V:
      return outer(inner(val))
    return composer

  @staticmethod
  def optional(fn: Callable[[T], U]) -> Callable[[Optional[T]], Optional[U]]:
    '''Returns a function that will return None if given None, otherwise maps the value with fn.'''
    def optionaler(val: Optional[T]) -> Optional[U]:
      if val is None:
        return None
      return fn(val)
    return optionaler

  @staticmethod
  def date(val: Date) -> str:
    '''date to ISO format.'''
    return val.isoformat()

  @staticmethod
  def datetime(val: DateTime) -> str:
    '''datetime to ISO format.'''
    return val.isoformat()

  @staticmethod
  def uuid(val: UUID) -> str:
    '''UUID to string.'''
    return str(val)

  @staticmethod
  def decimal(val: Decimal) -> str:
    '''Decimal number to string.'''
    return str(val)

  @staticmethod
  def bytes(val: Bytes) -> str:
    '''Bytes to b64 string.'''
    return b64encode(val).decode('utf-8')

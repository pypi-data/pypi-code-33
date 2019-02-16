from copy import deepcopy
from itertools import islice
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, TypeVar, Union

T = TypeVar('T')


def tap(function: Callable[[T], None]) -> Callable[[Any], T]:
    """
    Pipeline Tap Function.

    Takes whatever value in the pipeline, passes it to a procedure, and returns the
    original value.

    Great for debugging or for side-effects.

    >>> tap(print)('test')
    test
    'test'
    >>> tap(lambda x: print(f"The value of the pipeline is {x}"))('test')
    The value of the pipeline is test
    'test'
    """

    def _inner(value: T) -> T:
        function(deepcopy(value))
        return value

    return _inner

def _clean_key(key: str) -> Union[str, int]:
    return int(key) if key.isdigit() else key

def _key_to_keypath(key: Union[List[str], str]) -> List[Union[int, str]]:
    if "." in key:
        keypath = list(map(_clean_key, str(key).split('.')))
    elif isinstance(key, (tuple, list)):
        keypath = list(map(_clean_key, key))
    else:
        keypath = [key]
    return keypath

def lens(key: Union[List[str], str]) -> Callable[[Union[object, Dict[str, Any]]], Any]:
    """
    Dig Deeper into a object or dict.

    Given a key, list of keys, or a `.` separated key path, return a function that
    pulls that value from a given data structure, or returns None.

    Examples:
    >>> lens('a')({'a': 'foo'})
    'foo'
    >>> lens('a.b')({'a':{'b':'bar'}})
    'bar'
    >>> lens(['a', 'b'])({'a':{'b':'bar'}})
    'bar'
    >>> lens('a.0')({'a':['foo', 'bar']})
    'foo'
    """

    def _inner(target: Union[object, Dict[str, Any]]) -> Any:
        keypath = _key_to_keypath(key)
        _data = deepcopy(target)
        while keypath and _data is not None:
            k = keypath.pop(0)
            if isinstance(k, int) and isinstance(_data, (list, tuple)):
                _data = index(k)(_data)
            elif isinstance(_data, dict):
                _data = _data.get(str(k), None)
            else:
                _data = getattr(_data, str(k), None)
        return _data

    return _inner


def sort(key_func: Callable[[Any], bool], reverse: bool = False) -> Callable[[Iterable[T]], Iterable[T]]:
    """
    Partial Application Shortcut for the Sorted Function.
    The outer function takes the key function and reverse
    returning an inner function that applies it to a given iterable.

    Examples:

    >>> sort(lambda x: x)([3,1,2])
    [1, 2, 3]
    >>> sort(lambda x: x, reverse=True)([3,1,2])
    [3, 2, 1]
    """

    def _inner(values: Iterable) -> Iterable:
        return sorted(values, key=key_func, reverse=reverse)

    return _inner


def take(n: int) -> Callable[[Iterable[T]], Iterable[T]]:
    """
    Take the first n items from an iterable.

    Example:
    >>> list(take(2)([1,2,3,4,5]))
    [1, 2]
    >>> list(take(2)(range(1,100)))
    [1, 2]
    """

    def _inner(iterable: Iterable) -> Iterable:
        return islice(iterable, n)

    return _inner


def clone(value: T) -> Tuple[T, T]:
    """
    Takes a value and returns a tuple of two of it

    Example:
    >>> clone(1)
    (1, 1)
    >>> clone('foo')
    ('foo', 'foo')
    """
    return (value, value)


def index(i: int) -> Callable[[Sequence[T]], Optional[T]]:
    """
    Get the index of a Sequence and return it or None

    >>> index(1)([1,2,3])
    2
    >>> index(5)([1,2,3])
    """

    def _inner(seq: Sequence[T]) -> Optional[T]:
        try:
            return seq[i]
        except IndexError:
            return None

    return _inner


def contains(needle: T) -> Callable[[Iterable[T]], bool]:
    """
    A contains predicate builder. Returns a function that checks for the existance
    in another set.

    >>> contains(1)([1,2,3])
    True
    >>> contains(0)([1,2,3])
    False
    """

    def _inner(haystack: Iterable[T]) -> bool:
        return needle in haystack

    return _inner


def join(glue: str) -> Callable[[Iterable[str]], str]:
    """
    Wrapper around join.

    >>> join(',')(['1', '2', '3'])
    '1,2,3'
    """

    def _inner(parts: Iterable[str]) -> str:
        return glue.join(parts)

    return _inner


def flatten(nested: Iterable[Iterable[T]]) -> Iterable[T]:
    """
    Flatten an iterable of iterables

    >>> list(flatten([[1,2,3], [4,5,6], [7,8,9]]))
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return (t for iterable in nested for t in iterable)

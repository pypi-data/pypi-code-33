from copy import deepcopy
from itertools import islice
from typing import Any, Tuple, Callable, Dict, Iterable, TypeVar, Optional, Sequence

T = TypeVar('T')


def tap(function: Callable[[T], None], value: T) -> T:
    function(deepcopy(value))
    return value


def lens(key: str) -> Callable[[Dict[str, Any]], Any]:
    def inner(target: Dict[str, Any]) -> Any:
        return target[key]

    return inner


def sort(key_func: Callable[[Any], bool], values: Iterable) -> list:
    return sorted(values, key=key_func)


def take(n: int, iterable: Iterable) -> Iterable:
    return islice(iterable, n)


def clone(value: T) -> Tuple[T, T]:
    return (value, value)


def index(i: int) -> Callable[[Iterable[T]], Optional[T]]:
    def _inner(iter: Iterable[T]) -> Optional[T]:
        try:
            return iter[i]
        except IndexError:
            return None

    return _inner


def contains(needle: T) -> Callable[[Iterable[T]], bool]:
    def _inner(haystack: Iterable[T]) -> bool:
        return needle in haystack

    return _inner


def length(lenable: Sequence) -> int:
    return lenable.__len__()

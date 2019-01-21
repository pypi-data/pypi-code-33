import math
from functools import partial
from typing import List  # noqa: F401
from typing import Optional as Opt, Union

import hypothesis.strategies as hs
from hypothesis.internal.floats import next_down, next_up
from hypothesis.searchstrategy import SearchStrategy

from ._utils import ensure_not_integer, validate_bool, wrap
from .errors import InvalidArgument, InvalidArgumentValue
from .typing import JSON, Primitive


def _null() -> SearchStrategy[None]:
    return hs.none()


def _booleans() -> SearchStrategy[bool]:
    return hs.booleans()


def _integers(
    min_value: int = -(2 ** 53), max_value: int = +(2 ** 53)
) -> SearchStrategy[int]:
    assert isinstance(min_value, int)
    assert isinstance(max_value, int)
    assert min_value <= max_value
    return hs.integers().map(partial(wrap, min_value, max_value))


def _numbers(
    *, infs: bool = True, nan: bool = True, integers: bool = True
) -> SearchStrategy[Union[float, int]]:
    assert isinstance(infs, bool)
    assert isinstance(nan, bool)
    assert isinstance(integers, bool)
    if integers:
        ints = _integers()
        return hs.one_of(
            ints,
            ints.map(float),
            hs.floats(allow_infinity=infs, allow_nan=nan),
        )
    fints = _integers(-(2 ** 52) - 1, +(2 ** 52) + 1).map(float)
    return hs.one_of(
        fints.map(next_down),
        fints.map(next_up),
        hs.floats(allow_infinity=infs, allow_nan=nan).map(ensure_not_integer),
    )


def _strings() -> SearchStrategy[str]:
    return hs.one_of(
        hs.sampled_from(
            [
                "null",
                "None",
                "true",
                "True",
                "false",
                "False",
                "-Infinity",
                "-inf",
                "Infinity",
                "inf",
                "NaN",
                "nan",
            ]
        ),
        _numbers().map(str),
        hs.text(),
    )


def primitives(
    *,
    default: bool = True,
    null: Opt[bool] = None,
    booleans: Opt[bool] = None,
    numbers: Opt[bool] = None,
    infs: Opt[bool] = None,
    nan: Opt[bool] = None,
    integers: Opt[bool] = None,
    strings: Opt[bool] = None
) -> SearchStrategy[Primitive]:
    """Strategy to generate JSON primitives."""
    validate_bool(default)
    validate_bool(null, optional=True)
    validate_bool(booleans, optional=True)
    validate_bool(numbers, optional=True)
    validate_bool(infs, optional=True)
    validate_bool(nan, optional=True)
    validate_bool(integers, optional=True)
    validate_bool(strings, optional=True)
    if null is None:
        null = default
    if booleans is None:
        booleans = default
    if numbers is None:
        numbers = default
    if infs is None:
        infs = numbers
    if nan is None:
        nan = numbers
    if integers is None:
        integers = numbers
    if strings is None:
        strings = default
    args = []  # type: List[SearchStrategy[Primitive]]
    if null:
        args.append(_null())
    if booleans:
        args.append(_booleans())
    if numbers:
        args.append(_numbers(infs=infs, nan=nan, integers=integers))
    else:
        if nan:
            args.append(hs.just(math.nan))
        if infs:
            args.append(hs.sampled_from([-math.inf, +math.inf]))
        if integers:
            args.append(_integers())
    if strings:
        args.append(_strings())
    return hs.one_of(*args)


def jsons(
    *,
    default: bool = True,
    arrays: Opt[bool] = None,
    objects: Opt[bool] = None,
    max_leaves: int = 100,
    null: Opt[bool] = None,
    booleans: Opt[bool] = None,
    numbers: Opt[bool] = None,
    infs: Opt[bool] = None,
    nan: Opt[bool] = None,
    integers: Opt[bool] = None,
    strings: Opt[bool] = None
) -> SearchStrategy[JSON]:
    """Strategy to generate JSONs."""
    validate_bool(default)
    validate_bool(arrays, optional=True)
    validate_bool(objects, optional=True)
    if arrays is None:
        arrays = default
    if objects is None:
        objects = default
    if not isinstance(max_leaves, int):
        raise InvalidArgument()
    if max_leaves < 0:
        raise InvalidArgumentValue()
    base = primitives(
        default=default,
        null=null,
        booleans=booleans,
        numbers=numbers,
        infs=infs,
        nan=nan,
        integers=integers,
        strings=strings,
    )
    extend = None
    if arrays and objects:
        extend = lambda cs: hs.one_of(  # noqa: E731
            hs.lists(cs), hs.dictionaries(_strings(), cs)
        )
    elif arrays:
        extend = hs.lists
    elif objects:
        extend = partial(hs.dictionaries, _strings())
    if extend:
        return hs.recursive(base, extend, max_leaves=max_leaves)
    return base

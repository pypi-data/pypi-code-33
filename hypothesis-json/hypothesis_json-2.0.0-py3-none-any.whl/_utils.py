from math import isinf, isnan
from typing import Any

from hypothesis.internal.floats import next_down, next_up

from .errors import InvalidArgument, InvalidArgumentValue


def validate_bool(x: Any, *, optional: bool = False) -> None:
    """Raise iff x is not a bool."""
    assert isinstance(optional, bool)
    if x is None:
        if not optional:
            raise InvalidArgument()
    else:
        if not isinstance(x, bool):
            raise InvalidArgumentValue()


def wrap(i_min: int, i_max: int, i: int) -> int:
    """Wrap i between i_min and i_max."""
    assert isinstance(i_min, int)
    assert isinstance(i_max, int)
    assert isinstance(i, int)
    assert i_min <= i_max
    i_range = (i_max + 1) - i_min
    return (((i - i_min) % i_range) + i_range) % i_range + i_min


def ensure_not_integer(f: float) -> float:
    """Iff f is an integer return the closest float."""
    assert isinstance(f, float)
    if not (isinf(f) or isnan(f)):
        i = int(f)
        if f == i:
            i = wrap(-(2 ** 52), +(2 ** 52), i)
            if i < 0:
                f = next_up(float(i))  # type: ignore
            else:
                f = next_down(float(i))  # type: ignore
            assert isinstance(f, float)
        assert f != int(f)
    return f

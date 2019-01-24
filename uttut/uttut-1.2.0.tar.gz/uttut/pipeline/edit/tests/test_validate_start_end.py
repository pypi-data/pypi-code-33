import pytest

from ..validation import _validate_start_end


def test_normal():
    _validate_start_end(1, 3)


@pytest.mark.parametrize(
    "start,end",
    [
        pytest.param(12.3, 15, id='float_start'),
        pytest.param(12, 15.7, id='float_end'),
        pytest.param(12.3, 15.7, id='all_float'),
        pytest.param('start', 'end', id='all_str'),
    ],
)
def test_wrong_type(start, end):
    with pytest.raises(TypeError):
        _validate_start_end(start, end)


@pytest.mark.parametrize(
    "start,end",
    [
        pytest.param(-3, 10, id='start'),
        pytest.param(0, -7, id='end'),
        pytest.param(-19, -15, id='all'),
    ],
)
def test_negative(start, end):
    with pytest.raises(ValueError):
        _validate_start_end(start, end)


def test_end_smaller_than_start():
    with pytest.raises(ValueError):
        _validate_start_end(18, 10)

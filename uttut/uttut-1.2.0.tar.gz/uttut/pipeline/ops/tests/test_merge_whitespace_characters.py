import pytest

from .common_tests import common_test, update_locals
from ..merge_whitespace_characters import MergeWhiteSpaceCharacters


@pytest.fixture
def op():
    yield MergeWhiteSpaceCharacters()


test_cases = [
    pytest.param(
        " \t\n\r\x0b\x0c ",
        [0, 0, 0, 0, 0, 0, 0],
        " ",
        [0],
        id='all whitespace characters',
    ),
    pytest.param(
        " _int_   _int_   _int_ ",
        [0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0],
        " _int_ _int_ _int_ ",
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
        id='result of int token with space op',
    ),
    pytest.param(
        "GB亂入  _int_  次",
        [1, 1, 2, 2, 0, 0, 3, 3, 3, 3, 3, 0, 0, 4],
        "GB亂入 _int_ 次",
        [1, 1, 2, 2, 0, 3, 3, 3, 3, 3, 0, 4],
        id='zh + int token',
    ),
    pytest.param(
        "我想要喝多 多 綠",
        [0, 0, 0, 0, 1, 1, 1, 1, 1],
        "我想要喝多 多 綠",
        [0, 0, 0, 0, 1, 1, 1, 1, 1],
        id='label identity',
    ),
    pytest.param(
        "GB亂入",
        [1, 1, 2, 2],
        "GB亂入",
        [1, 1, 2, 2],
        id='identity',
    ),
]


funcs = common_test(test_cases)
update_locals(locals(), funcs)


def test_equal(op):
    assert MergeWhiteSpaceCharacters() == op

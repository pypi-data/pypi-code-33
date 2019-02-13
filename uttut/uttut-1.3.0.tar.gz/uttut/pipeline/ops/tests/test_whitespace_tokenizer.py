import pytest

from ..whitespace_tokenizer import WhiteSpaceTokenizer
from .common_tests import common_test, update_locals


@pytest.fixture
def op():
    yield WhiteSpaceTokenizer()


test_cases = [
    pytest.param(
        "a \t \t \nb c",
        [1, 0, 0, 0, 0, 0, 0, 2, 0, 3],
        ["a", "b", "c"],
        [1, 2, 3],
        id='eng',
    ),
    pytest.param(
        "  a \t \t \nb c\n\r",
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 3, 0, 0],
        ["a", "b", "c"],
        [1, 2, 3],
        id='eng with whitespace at head and tail',
    ),
    pytest.param(
        "GB亂入",
        [2, 2, 2, 2],
        ["GB亂入"],
        [2],
        id='zh',
    ),
    pytest.param(
        "",
        [],
        [],
        [],
        id='empty string',
    ),
]


funcs = common_test(test_cases)
update_locals(locals(), funcs)


def test_equal(op):
    assert WhiteSpaceTokenizer() == op

import pytest

from .common_tests import common_test, update_locals
from ..strip_whitespace_characters import StripWhiteSpaceCharacters


@pytest.fixture
def op():
    yield StripWhiteSpaceCharacters()


test_cases = [
    pytest.param(
        " \t\n\r\x0b\x0c ",
        [0, 0, 0, 0, 0, 0, 0],
        "",
        [],
        id='all whitespace characters',
    ),
    pytest.param(
        " abc \n\t ",
        [0, 1, 1, 1, 0, 0, 0, 0],
        "abc",
        [1, 1, 1],
        id='eng with whitespaces',
    ),
    pytest.param(
        "我想要喝多 多 綠",
        [0, 0, 0, 0, 1, 1, 1, 1, 1],
        "我想要喝多 多 綠",
        [0, 0, 0, 0, 1, 1, 1, 1, 1],
        id='inner whitespace',
    ),
    pytest.param(
        "GB亂入",
        [1, 1, 2, 2],
        "GB亂入",
        [1, 1, 2, 2],
        id='identity',
    ),
    pytest.param(
        "",
        [],
        "",
        [],
        id='empty string',
    ),
]


funcs = common_test(test_cases)
update_locals(locals(), funcs)


def test_all_whitespaces(op):
    # labels are not invertible
    output_seq, output_labels, realigner = op.transform(
        "  \n\n\t\t",
        [1, 2, 3, 4, 5, 6],
    )
    assert "" == output_seq
    assert [] == output_labels

    output = realigner([])
    assert output == [0, 0, 0, 0, 0, 0]


def test_equal(op):
    assert StripWhiteSpaceCharacters() == op

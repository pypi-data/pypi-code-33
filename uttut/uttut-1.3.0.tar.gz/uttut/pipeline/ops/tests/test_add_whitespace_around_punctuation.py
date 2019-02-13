import pytest

from ..add_whitespace_around_punctuation import AddWhitespaceAroundPunctuation
from .common_tests import common_test, update_locals


@pytest.fixture
def op():
    yield AddWhitespaceAroundPunctuation()


test_cases = [
    pytest.param(
        "^$`",
        [1, 2, 3],
        " ^  $  ` ",
        [0, 1, 0, 0, 2, 0, 0, 3, 0],
        id='punct in range',
    ),
    pytest.param(
        "⁕⁇※࡞",  # These are just a small portion of punctuations in P category.
        [1, 2, 3, 4],
        " ⁕  ⁇  ※  ࡞ ",
        [0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0],
        id='puncts in P category only',
    ),
    pytest.param(
        "a,b",
        [1, 2, 3],
        "a , b",
        [1, 0, 2, 0, 3],
        id='eng',
    ),
    pytest.param(
        "隼興亂入",
        [2, 3, 4, 5],
        "隼興亂入",
        [2, 3, 4, 5],
        id='all chinese',
    ),
]


funcs = common_test(test_cases)
update_locals(locals(), funcs)


def test_equal(op):
    assert op == AddWhitespaceAroundPunctuation()

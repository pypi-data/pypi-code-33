import pytest

from ..add_whitespace_around_cjk import AddWhitespaceAroundCJK
from .common_tests import common_test, update_locals


@pytest.fixture
def op():
    yield AddWhitespaceAroundCJK()


test_cases = [
    pytest.param(
        "alvin喜歡吃榴槤",
        [1, 1, 1, 1, 1, 2, 3, 4, 5, 6],
        "alvin 喜  歡  吃  榴  槤 ",
        [1, 1, 1, 1, 1, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 6, 0],
        id='eng + zh',
    ),
    pytest.param(
        "hello! how are you?",
        [1, 1, 1, 1, 1, 2, 0, 3, 3, 3, 0, 4, 4, 4, 0, 5, 5, 5, 6],
        "hello! how are you?",
        [1, 1, 1, 1, 1, 2, 0, 3, 3, 3, 0, 4, 4, 4, 0, 5, 5, 5, 6],
        id='eng',
    ),

]


funcs = common_test(test_cases)
update_locals(locals(), funcs)


def test_equal(op):
    assert op == AddWhitespaceAroundCJK()

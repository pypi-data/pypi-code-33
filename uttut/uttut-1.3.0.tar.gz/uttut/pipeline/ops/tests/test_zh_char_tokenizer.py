import pytest

from ..zh_char_tokenizer import ZhCharTokenizer
from .common_tests import common_test, update_locals


@pytest.fixture
def op():
    return ZhCharTokenizer()


test_cases = [
    pytest.param(
        "How's it going today, Mr.Smith?",
        [1, 1, 1, 1, 1, 0, 2, 2, 0, 3, 3, 3, 3, 3, 0, 4, 4, 4, 4, 4, 5, 0,
         6, 6, 6, 6, 6, 6, 6, 6, 7],
        ['How', "'", 's', 'it', 'going', 'today', ',', 'Mr', '.', 'Smith', '?'],
        [1, 1, 1, 2, 3, 4, 5, 6, 6, 6, 7],
        id='eng',
    ),
    pytest.param(
        "薄餡的櫻花妹呢？",
        [1, 1, 0, 2, 2, 2, 3, 4],
        ['薄', '餡', '的', '櫻', '花', '妹', '呢', '？'],
        [1, 1, 0, 2, 2, 2, 3, 4],
        id='zh',
    ),
    pytest.param(
        "GB亂入",
        [1, 1, 2, 2],
        ['GB', '亂', '入'],
        [1, 2, 2],
        id='eng + zh',
    ),
    pytest.param(
        "GB亂入!!!",
        [1, 1, 2, 2, 3, 4, 5],
        ['GB', '亂', '入', '!', '!', '!'],
        [1, 2, 2, 3, 4, 5],
        id='eng + zh + punct',
    ),
]


funcs = common_test(test_cases)
update_locals(locals(), funcs)


def test_equal(op):
    assert op == ZhCharTokenizer()

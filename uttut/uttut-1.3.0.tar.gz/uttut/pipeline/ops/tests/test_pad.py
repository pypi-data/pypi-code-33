import pytest

from ..pad import Pad
from ..tokens import PAD_TOKEN
from .common_tests import common_test, update_locals


@pytest.fixture
def op():
    yield Pad(5)


test_cases = [
    pytest.param(
        ['alvin', '喜歡', '吃', '榴槤', '!'],
        [1, 2, 3, 4, 5],
        ['alvin', '喜歡', '吃', '榴槤', '!'],
        [1, 2, 3, 4, 5],
        id='equal',
    ),
    pytest.param(
        ['alvin'],
        [1],
        ['alvin', PAD_TOKEN, PAD_TOKEN, PAD_TOKEN, PAD_TOKEN],
        [1, 0, 0, 0, 0],
        id='shorter',
    ),
]


funcs = common_test(test_cases)
update_locals(locals(), funcs)


def test_longer_case(op):
    # labels are not invertible
    output_seq, label_aligner = op.transform(
        ['alvin', '喜歡', '吃', '榴槤', '和', '蟲', '!'],
    )
    assert ['alvin', '喜歡', '吃', '榴槤', '和'] == output_seq

    output_labels = label_aligner.transform([1, 2, 3, 4, 5, 6, 7])
    assert [1, 2, 3, 4, 5] == output_labels

    output = label_aligner.inverse_transform(output_labels)
    assert [1, 2, 3, 4, 5, 0, 0] == output


def test_equal(op):
    assert Pad(5) == op


def test_not_equal():
    op1 = Pad(pad_token='PAD', maxlen=10)
    op2 = Pad(pad_token='PAD', maxlen=15)
    op3 = Pad(maxlen=10)
    assert op1 != op2
    assert op2 != op3

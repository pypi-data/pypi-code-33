import pytest

from ..span_subwords import SpanSubwords
from .common_tests import common_test


def to_dict(input_list):
    output_dict = {}
    for i, token in enumerate(input_list):
        output_dict[token] = i
    return output_dict


test_cases_pair = [
    {
        "tokenizer": SpanSubwords(
            vocab=to_dict(["I", "like", "apples"]),
            unk_token="<unk>",
            maxlen_per_token=10,
        ),
        "prefix": "no-subwords",
        "cases": {
            "exactly match": (
                ["I", "like", "apples"],
                [1, 2, 3],
                ["I", "like", "apples"],
                [1, 2, 3],
            ),
            "word not found": (
                ["I", "like", "bananas"],
                [1, 2, 3],
                ["I", "like", "<unk>"],
                [1, 2, 3],
            ),
            "word too long": (
                ["Ilikebananas"],
                [3],
                ["<unk>"],
                [3],
            ),
        },
    },
    {
        "tokenizer": SpanSubwords(
            vocab=to_dict(["[UNK]", "[CLS]", "[SEP]", "want",
                           "##want", "##ed", "wa", "un", "runn", "##ing"]),
            unk_token="[UNK]",
            maxlen_per_token=200,
        ),
        "prefix": "has-subwords",
        "cases": {
            "exactly match": (
                ["unwanted", "running"],
                [1, 2],
                ["un", "##want", "##ed", "runn", "##ing"],
                [1, 1, 1, 2, 2],
            ),
            "word not found":(
                ["unwantedX", "running"],
                [1, 2],
                ["[UNK]", "runn", "##ing"],
                [1, 2, 2],
            ),
        },
    },
]


@pytest.mark.parametrize(  # type: ignore
    "tokenizer,test_case",
    [
        pytest.param(category["tokenizer"], case, id=f"{category['prefix']}_{case_id}")
        for category in test_cases_pair
        for case_id, case in category["cases"].items()  # type: ignore
    ],
)
def test_all(tokenizer, test_case):
    funcs = common_test(test_case)
    for func in funcs:
        func(*test_case, tokenizer)


@pytest.mark.parametrize(
    "obj1,obj2",
    [
        pytest.param(
            SpanSubwords(
                vocab=to_dict(["I", "like", "apples"]),
                unk_token="<unk>",
                maxlen_per_token=10,
            ),
            SpanSubwords(
                vocab=to_dict(["I", "like", "apples"]),
                unk_token="<unk>",
                maxlen_per_token=200,
            ),
            id="different maxlen_per_token",
        ),
        pytest.param(
            SpanSubwords(
                vocab=to_dict(["I", "like", "apples"]),
                unk_token="<unk>",
                maxlen_per_token=10,
            ),
            SpanSubwords(
                vocab=to_dict(["I", "like", "apples"]),
                unk_token="[UNK]",
                maxlen_per_token=10,
            ),
            id="different unk",
        ),
        pytest.param(
            SpanSubwords(
                vocab=to_dict(["I", "like", "apples"]),
                unk_token="<unk>",
                maxlen_per_token=10,
            ),
            SpanSubwords(
                vocab=to_dict(["##apples"]),
                unk_token="<unk>",
                maxlen_per_token=10,
            ),
            id="different vocab",
        ),
    ],
)
def test_not_equal(obj1, obj2):
    assert obj1 != obj2

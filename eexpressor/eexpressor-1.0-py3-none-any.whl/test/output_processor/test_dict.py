import pytest
from src.output_processor import dict


@pytest.mark.parametrize('test_input, expected', [
    ('화나다', "성이 나서 화기 가 생기다"),
    ('angry', "Feeling or showing strong annoyance, displeasure, or\
 hostility; full of anger.")
    ])
def test_dict_test(test_input, expected):
    assert dict.get_output(test_input) == expected

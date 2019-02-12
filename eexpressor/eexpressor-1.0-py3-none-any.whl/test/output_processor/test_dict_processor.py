import pytest
from src.output_processor import dict_processor


@pytest.mark.parametrize('test_input, test_lang, expected', [
    ('화나다', 'kor', "성이 나서 화기 가 생기다"),
    ('angry', 'eng', "Feeling or showing strong annoyance, displeasure, or\
 hostility; full of anger.")
    ])
def test_dict_processor_test(test_input, test_lang, expected):
    assert dict_processor.get_output(test_input, test_lang) == expected

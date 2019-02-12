import pytest
from src.output_processor import translate


@pytest.mark.parametrize('test_input, expected', [
    ('화나다', 'angry'),
    ('怒った', 'Angry'),
    ('en colère', 'angry')
    ])
def test_translate(test_input, expected):
    assert translate.get_output(test_input) == expected

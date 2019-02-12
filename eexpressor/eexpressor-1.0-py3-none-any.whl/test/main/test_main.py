import pytest
from src.main import main


@pytest.mark.parametrize("test_input, expected", [
    (main.get_parser().parse_args(['화나다']), "성이 나서 화기 가 생기다"),
    (main.get_parser().parse_args(['angry']), "Feeling or showing strong \
annoyance, displeasure, or hostility; full of anger.")
    ])
def test_main_test(test_input, expected):
    assert main.main(test_input) == expected

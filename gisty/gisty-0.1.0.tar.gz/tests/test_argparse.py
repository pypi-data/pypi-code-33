import pytest

# from gisty.gists import main
from gisty.conf import parse_configuration


def test_argparsing(capsys):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        parse_configuration('')
    assert pytest_wrapped_e.type == SystemExit
    msg = 'the following arguments are required: username'
    captured = capsys.readouterr()
    assert msg in captured.err

import sys
import pytest
import conficus
from conficus import coerce


if (sys.version_info.major < 3 and sys.version_info.minor < 4) \
        or sys.version_info.major == 2:
    from pathlib2 import Path
else:
    from pathlib import Path  # noqa


def test_handle_custom_coercers_with_regex_error(capsys):
    with pytest.raises(Exception) as ex:
        [c for c in coerce.handle_custom_coercers([('int', ('^\d+$', str))])]

    assert 'must contain a named group' in str(ex.value)


def test_handle_custom_coercers_with_converter_error():
    with pytest.raises(Exception) as ex:
        [c for c in coerce.handle_custom_coercers([('int', ('^(?P<value>\d+)$', '4'))])]
    assert 'must be callable' in str(ex.value)


def test_coerce_custom_replacement():
    config = conficus.load('integer = 5')
    assert config['integer'] == 5

    config = conficus.load('integer = 5', coercers=[('int', ('^(?P<value>\d+)$', str))])
    assert config['integer'] == '5'


def test_coerce_custom_additional():
    config = conficus.load('integer = 5')
    assert config['integer'] == 5
    config = conficus.load('integer = 5', coercers=[('myint', ('^(?P<value>\d+)$', str))])
    assert config['integer'] == '5'


def test_coerce_custom_additional_2():
    pass

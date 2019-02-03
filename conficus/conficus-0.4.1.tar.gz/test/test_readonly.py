import pytest
from conficus.parse import ConfigDict
from conficus.readonly import ReadOnlyDict


def test_readonly_dict():
    d = ConfigDict()
    d['one'] = ConfigDict()
    d['one']['name'] = 'one'
    d['one']['two'] = ConfigDict()
    d['one']['two']['name'] = 'one two'

    d = ReadOnlyDict(d)

    assert 'one' in d
    assert 'two' not in d
    assert 'one.two' in d
    assert 'one.three' not in d
    assert 'one.two.name' in d
    assert 'one.two.who' not in d

    assert d['one.name'] == 'one'
    assert d['one.two.name'] == 'one two'

    with pytest.raises(TypeError):
        d['new item'] = 'foo'

    with pytest.raises(TypeError):
        d['one']['two']['new item'] = 'foo'

    with pytest.raises(TypeError):
        d['one'].pop('name')

    with pytest.raises(TypeError):
        del d['one']['name']

    with pytest.raises(TypeError):
        d['one'].popitem()

    with pytest.raises(TypeError):
        d.clear()

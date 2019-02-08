from hjs import hjs, dumps, loads

from pkg_resources import resource_string
try:
    # py2
    unicode
except NameError:
    import codecs
    # py3
    resource_bytes = resource_string

    def resource_string(*args, **kw):
        bytes = resource_bytes(*args, **kw)
        return codecs.decode(bytes)


def test_hjs_from_json_resource():
    raw = resource_string(__name__, "universe.json")
    data = loads(raw)
    trip = dumps(data)
    assert raw == trip + '\n'


def test_hjs_from_hson_resource():
    raw = resource_string(__name__, "universe.hjson")
    data = loads(raw)
    trip = dumps(data)
    assert raw == trip + '\n'


def test_hjs_dict_shadowed():
    data = hjs("""
    {
        values: [1, 2, 3]
        keys: [4, 5, 6]
    }""")
    assert data['values'] == [1, 2, 3]
    assert data['keys'] == [4, 5, 6]
    assert list(data.values()) == [[1, 2, 3], [4, 5, 6]]
    assert list(data.keys()) == ['values', 'keys']

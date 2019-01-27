import json

from cashmere import backends
from cashmere import serializers
from cashmere import autoserial


def test_json_serialize_list():
    codec = autoserial.AutoCodec()
    codec.register(autoserial.ValueCodec(list, dump=json.dump, load=json.load))
    cache = backends.DirectoryCache(codec=codec)

    lst = [1, 2, 3]

    @cache.cache_call
    def f():
        return lst

    assert f() == lst

    assert f() == lst

import json

import pytest

from cashmere import backends
from cashmere import serializers
from cashmere import autoserial


def test_json_serialize_list():
    codec = autoserial.AutoCodec()
    codec.register(autoserial.ValueCodec(list, dump=json.dump, load=json.load))
    cache = backends.DirectoryCache(codec=codec)

    lst = [1, 2, 3]

    @cache.memoize
    def f():
        return lst

    assert f() == lst

    assert f() == lst


def test_json_serialize_fail():
    codec = autoserial.AutoCodec()
    cache = backends.DirectoryCache(codec=codec)

    lst = [1, 2, 3]

    @cache.memoize
    def f():
        return lst

    with pytest.raises(KeyError):
        assert f() == lst

    with pytest.raises(KeyError):
        assert f() == lst

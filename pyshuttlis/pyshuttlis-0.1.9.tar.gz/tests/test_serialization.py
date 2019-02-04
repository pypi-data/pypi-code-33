from uuid import uuid4

from shuttlis.serialization import serialize


def test_serialize_with_None():
    res = serialize(None)
    assert res is None


def test_serialize_with_uuid():
    uuid = uuid4()
    res = serialize(uuid)
    assert str(uuid) == res


def test_serialize_with_byte_array():
    bytes = b"Hey Dude!!!!"
    res = serialize(bytes)
    assert "Hey Dude!!!!" == res

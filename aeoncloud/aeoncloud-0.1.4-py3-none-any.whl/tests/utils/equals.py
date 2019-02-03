import json


def dict_equals(a, b) -> None:
    a_dump = json.dumps(a, sort_keys=True)
    b_dump = json.dumps(b, sort_keys=True)

    assert a_dump == b_dump

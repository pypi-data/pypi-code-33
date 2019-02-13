from eggit.egg_string import random_string


def test_random_string():
    result1 = random_string(4)
    result2 = random_string(8)
    result3 = random_string(64)

    assert len(result1) == 4
    assert len(result2) == 8
    assert len(result3) == 64

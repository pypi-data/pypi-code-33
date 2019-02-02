from smallerize.utils import (
    _dict_add_inplace,
    _dict_div_inplace,
    _dict_product_inplace
)


def test_dict_add_inplace():
    a = {'x': 1, 'y': 2}
    b = {'y': 3, 'x': 4}
    _dict_add_inplace(a, b)
    assert a['x'] == 5
    assert a['y'] == 5


def test_dict_div_inplace():
    a = {'x': 10, 'y': 9}
    b = {'x': 2, 'y': 3}
    _dict_div_inplace(a, b)
    assert a['x'] == 5
    assert a['y'] == 3


def test_dict_product_inplace():
    a = {'x': 5, 'y': 3}
    b = {'x': 2, 'y': 2}
    _dict_product_inplace(a, b)
    assert a['x'] == 10
    assert a['y'] == 6

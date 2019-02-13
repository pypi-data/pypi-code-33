from eggit.converters import Converter


def test_str_to_int():
    assert Converter.str_to_int('1') == 1
    assert Converter.str_to_int('1123') == 1123
    assert Converter.str_to_int('1.1') is None
    assert Converter.str_to_int('abc') is None


def test_tr_to_bool():
    assert Converter.str_to_bool('True')
    assert Converter.str_to_bool('true')
    assert Converter.str_to_bool('tRUe')  # random upper or lower
    assert not Converter.str_to_bool('False')
    assert not Converter.str_to_bool('false')
    assert not Converter.str_to_bool('fALse')
    assert not Converter.str_to_bool('Random String')

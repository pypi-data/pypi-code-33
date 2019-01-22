from thicc import thicc

wide_string = "Ｔｈｅ　ｑｕｉｃｋ　ｂｒｏｗｎ　ｆｏｘ　ｊｕｍｐｓ　ｏｖｅｒ　ｔｈｅ　ｌａｚｙ　ｄｏｇ．"
narrow_string = "The quick brown fox jumps over the lazy dog."


def test_widen():
    assert thicc.map_string(narrow_string) == wide_string


def test_narrow():
    assert thicc.map_string(wide_string, reverse=True) == narrow_string


def test_widen_already_wide():
    assert thicc.map_string(wide_string) == wide_string


def test_narrow_already_narrow():
    assert thicc.map_string(narrow_string, reverse=True) == narrow_string

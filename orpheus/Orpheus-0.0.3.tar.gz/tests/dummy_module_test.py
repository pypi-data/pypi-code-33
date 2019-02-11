from orpheus.util.dummy_module import multiply

def test_numbers_4_5():
    assert multiply(4,5) == 20

def test_string_b_4():
    assert multiply('b',4) == 'bbbb'

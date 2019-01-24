import markr
import os

def test_set_get(tmpdir):
    f = tmpdir.join('foo.txt')
    f.write('l')
    f_name = str(f)
    k, v = 'key', 'value'
    markr.set(f_name, k, v)
    attrs = markr.get(f_name)

    assert len(attrs) == 1
    attr = attrs[0]
    assert attr[0] == k
    assert attr[1] == v


def test_set_multiple(tmpdir):
    f = tmpdir.join('bar.txt')
    f.write('l')
    f_name = str(f)
    pairs = [('1', '2'), ('3', '4')]
    for k, v in pairs:
        markr.set(f_name, k, v)
        markr.set(f_name, k, v)

    attrs = markr.get(f_name)
    assert set(attrs) == set(pairs)

def test_set_no_value(tmpdir):
    f = tmpdir.join('bob.txt')
    f.write('l')
    f_name = str(f)
    k = 'key'
    markr.set(f_name, k)
    attrs = markr.get(f_name)

    assert len(attrs) == 1
    attr = attrs[0]
    assert attr[0] == k
    assert attr[1] == ''

def test_rm(tmpdir):
    f = tmpdir.join('baz.txt')
    f.write('l')
    f_name = str(f)
    k, v = 'key', 'value'
    markr.set(f_name, k, v)
    markr.rm(f_name, k)

    assert len(markr.get(f_name)) == 0


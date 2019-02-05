from crl.examplelib.examplelib import (
    example, other_example, Example, new_example)


__copyright__ = 'Copyright (C) 2019, Nokia'


def test_example(capsys):
    example()
    out, _ = capsys.readouterr()
    assert out == 'example called\n'


def test_other_example(capsys):
    other_example('example')
    out, _ = capsys.readouterr()
    assert out == 'example\n'


def test_example_class(capsys):
    Example('example').example()
    out, _ = capsys.readouterr()
    assert out == 'example\n'


def test_new_example():
    assert new_example() == 'new example in demo'

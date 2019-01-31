"""Unit test for utils.py."""

import mynotes
import os.path
import pytest
from . import tree


@pytest.mark.parametrize("inp, exp", [
    ((os.path.join(tree.TESTS_DIR, tree.ROOT), [], []),
     [(tree.ROOT, [tree.D1, tree.D2], [tree.FILE_W_TITLE, tree.FILE_W_TITLE]),
      (tree.ROOT_D1, [], [tree.FILE3, tree.FILE4]),
      (tree.ROOT_D2, [], [tree.FILE5, tree.FILE6]),
      ]),
    ((os.path.join(tree.TESTS_DIR, tree.ROOT), [tree.D1], []),
     [(tree.ROOT, [tree.D2], [tree.FILE_W_TITLE, tree.FILE_W_TITLE]),
      (tree.ROOT_D2, [], [tree.FILE5, tree.FILE6]),
      ]),
    ((os.path.join(tree.TESTS_DIR, tree.ROOT),
      [tree.D1, tree.D2], [tree.FILE_W_TITLE]),
     [(tree.ROOT, [], [tree.FILE_W_TITLE]),
      (tree.ROOT_D2, [], [tree.FILE5, tree.FILE6]),
      ]),
])
def test_walk(inp, exp):
    """Test walk function."""
    print(list(mynotes.utils.walk(inp[0], inp[1], inp[2])))
    r = zip(mynotes.utils.walk(inp[0], inp[1], inp[2]), exp)
    assert len(list(r)), 'Must be > 0'
    for x, e in r:
        assert x == e


@pytest.mark.parametrize("inp, exp", [
    # inp = Params(...)
    # exp = tuple containing all arguments of Params
    (mynotes.utils.Params(
        'index',
        'home',
        '.md',
        ['d1', 'd2'],
        ['f1', 'f2'],
        True),
     ('index',
      'home',
      '.md',
      ['d1', 'd2'],
      ['f1', 'f2'],
      True)),
    (mynotes.utils.Params(
        'index',
        'home',
        '.md',
        ['d1'],
        ['f1'],
        True),
     ('index',
      'home',
      '.md',
      ['d1'],
      ['f1'],
      True)),
    (mynotes.utils.Params(
        'index',
        'home',
        '.md',
        [],
        [],
        False),
     ('index',
      'home',
      '.md',
      [],
      [],
      False)),
])
def test_Params(inp, exp):
    """Test Params class."""
    assert inp.index == exp[0]
    assert inp.home == exp[1]
    assert inp.md_ext == exp[2]
    assert inp.excl_dirs == exp[3]
    assert inp.excl_files == exp[4]
    assert inp.verbose == exp[5]


@pytest.mark.parametrize("inp, exp", [
    (mynotes.utils.DataAbstract(
        'home file',
        'index file',
        'root dir',
        'file name',
        'file title'),
     ('home file',
      'index file',
      'root dir',
      'file name',
      'file title',
      'file title',  # for compare()
      False)),  # is home file == file name
    (mynotes.utils.DataAbstract(
        'Home FILE',
        'Index FILE',
        'Root DIR',
        'File NAME',
        'File TITLE'),
     ('Home FILE',
      'Index FILE',
      'Root DIR',
      'File NAME',
      'File TITLE',
      'file title',  # for compare()
      False)),  # is home file == file name
    (mynotes.utils.DataAbstract(
        'Home FILE',
        'Index FILE',
        'Root DIR',
        'Home FILE',
        'Home TITLE'),
     ('Home FILE',
      'Index FILE',
      'Root DIR',
      'Home FILE',
      'Home TITLE',
      'home title',  # for compare()
      True)),  # is home file == file name
])
def test_DataAbstract(inp, exp):
    """Test DataAbstract class."""
    assert inp._home == exp[0]
    assert inp._index == exp[1]
    assert inp.root == exp[2]
    assert inp.name == exp[3]
    assert inp.title == exp[4]
    assert inp.compare() == exp[5]
    assert inp.is_home_file() == exp[6]
    assert repr(inp) == f'DataAbstract(\'{exp[0]}\', \'{exp[1]}\', ' \
                        f'\'{exp[2]}\', \'{exp[3]}\', \'{exp[4]}\')'


@pytest.mark.parametrize("inp, exp", [
    (mynotes.utils.DataFile(
        'home file',
        'index file',
        'root dir',
        'file name',
        'file title'),
     ('home file',
      'index file',
      'root dir',
      'file name',
      'file title',
      'file title',  # for compare()
      False)),  # is home file == file name
    (mynotes.utils.DataFile(
        'Home FILE',
        'Index FILE',
        'Root DIR',
        'File NAME',
        'File TITLE'),
     ('Home FILE',
      'Index FILE',
      'Root DIR',
      'File NAME',
      'File TITLE',
      'file title',  # for compare()
      False)),  # is home file == file name
    (mynotes.utils.DataFile(
        'Home FILE',
        'Index FILE',
        'Root DIR',
        'Home FILE',
        'Home TITLE'),
     ('Home FILE',
      'Index FILE',
      'Root DIR',
      'Home FILE',
      'Home TITLE',
      'home title',  # for compare()
      True)),  # is home file == file name
])
def test_DataFile(inp, exp):
    """Test DataFile class."""
    assert inp._home == exp[0]
    assert inp._index == exp[1]
    assert inp.root == exp[2]
    assert inp.name == exp[3]
    assert inp.title == exp[4]
    assert inp.compare() == exp[5]
    assert inp.is_home_file() == exp[6]
    assert inp.link() == f'[{exp[4]}]({exp[3]})'
    assert repr(inp) == f'DataFile(\'{exp[0]}\', \'{exp[1]}\', ' \
                        f'\'{exp[2]}\', \'{exp[3]}\', \'{exp[4]}\')'


@pytest.mark.parametrize("inp, exp", [
    (mynotes.utils.DataDir(
        'home file',
        'index file',
        'root dir',
        'file name',
        'file title'),
     ('home file',
      'index file',
      'root dir',
      'file name',
      'file title',
      'file title',  # for compare()
      False)),  # is home file == file name
    (mynotes.utils.DataDir(
        'Home FILE',
        'Index FILE',
        'Root DIR',
        'File NAME',
        'File TITLE'),
     ('Home FILE',
      'Index FILE',
      'Root DIR',
      'File NAME',
      'File TITLE',
      'file title',  # for compare()
      False)),  # is home file == file name
    (mynotes.utils.DataDir(
        'Home FILE',
        'Index FILE',
        'Root DIR',
        'Home FILE',
        'Home TITLE'),
     ('Home FILE',
      'Index FILE',
      'Root DIR',
      'Home FILE',
      'Home TITLE',
      'home title',  # for compare()
      True)),  # is home file == file name
])
def test_DataDir(inp, exp):
    """Test DataDir class."""
    assert inp._home == exp[0]
    assert inp._index == exp[1]
    assert inp.root == exp[2]
    assert inp.name == exp[3]
    assert inp.title == exp[4]
    assert inp.compare() == exp[5]
    assert inp.is_home_file() == exp[6]
    assert inp.link() == f'[{exp[4]}]({exp[3]}/{exp[1]})'
    assert repr(inp) == f'DataDir(\'{exp[0]}\', \'{exp[1]}\', \'{exp[2]}\', ' \
                        f'\'{exp[3]}\', \'{exp[4]}\')'

"""Unit test for gen.py."""

import mynotes
import os.path
import pytest
from . import tree


prms = mynotes.utils.Params(
        'index.md',
        'home.md',
        '.md',
        ['excld1'],
        ['exclf1'],
        False)


@pytest.fixture()
def file_with_title(tmpdir_factory):
    """Create temporary file with title for _bi_process_file."""
    fn = tmpdir_factory.mktemp('data').join('file.md')
    with open(fn, 'w') as fpw:
        fpw.write('# File Title\n## H2\n...')
    return fn


@pytest.fixture()
def file_without_title(tmpdir_factory):
    """Create temporary file without title for _bi_process_file."""
    fn = tmpdir_factory.mktemp('data').join('file.md')
    with open(fn, 'w') as fpw:
        fpw.write('## H2\n...')
    return fn


@pytest.mark.parametrize("inp, exp", [
    ((os.path.join(tree.TESTS_DIR, tree.ROOT), tree.FILE_W_TITLE),
     ('File With Title')),
    ((os.path.join(tree.TESTS_DIR, tree.ROOT), tree.FILE_WO_TITLE),
     (tree.FILE_WO_TITLE)),
    ((os.path.join(tree.TESTS_DIR, tree.ROOT), tree.FILE_UNKNOWN),
     (None)),
])
def test__bi_process_file_(inp, exp):
    """Test _bi_process_file function."""
    r = mynotes.gen._bi_process_file(prms, inp[0], inp[1])
    if exp is None:
        assert r is None
    else:
        assert r is not None
        assert r.title == exp


@pytest.mark.parametrize("inp, exp", [
    ((os.path.join(tree.TESTS_DIR, tree.ROOT),
      [tree.FILE_W_TITLE, tree.FILE_WO_TITLE, tree.FILE_UNKNOWN]),
     (2, ['File With Title', tree.FILE_WO_TITLE])),
])
def test__bi_process_files(inp, exp):
    """Test _bi_process_files function."""
    rs = mynotes.gen._bi_process_files(prms, inp[0], inp[1])
    assert len(rs) == exp[0]
    for r, e in zip(rs, exp[1]):
        assert r is not None
        assert isinstance(r, mynotes.utils.DataFile)
        assert r.title == e


@pytest.mark.parametrize("inp, exp", [
    ((tree.ROOT, [tree.D1, tree.D2]),
     (2, ['d1', 'd 2'])),
])
def test__bi_process_dirs(inp, exp):
    """Test _bi_process_dirs function."""
    rs = mynotes.gen._bi_process_dirs(prms, inp[0], inp[1])
    assert len(rs) == exp[0]
    for r, e in zip(rs, exp[1]):
        assert r is not None
        assert isinstance(r, mynotes.utils.DataDir)
        assert r.title == e


# TODO def test__bi_gen_index():
#          """Test _bi_gen_index function."""
# TODO def test_build_index():
#          """Test build_index function."""
# TODO def _gh_md2html_gfm():
#          """Test _gh_md2html_gfm function."""
# TODO def _gh_css_gfm():
#          """Test _gh_css_gfm function."""
# TODO def _gh_copy_extra_dir():
#          """Test _gh_copy_extra_dir function."""
# TODO def _gh_process_file():
#          """Test _gh_process_file function."""
# TODO def generate_html():
#          """Test generate_html function."""

"""Unit test for config.py."""

import mynotes
import pytest


@pytest.fixture()
def empty_file(tmpdir_factory):
    """Create temporary empty configuration file."""
    fn = tmpdir_factory.mktemp('conf').join('empty')
    return fn


@pytest.fixture()
def non_empty_file(tmpdir_factory):
    """Create temporary non empty configuration file."""
    fn = tmpdir_factory.mktemp('conf').join('non_empty')
    exp = '[{:s}]\n'.format(mynotes.constants.PACKAGE_NAME) + \
          '{:s} = {:s}\n'.format(mynotes.config.Config.PRM_MD_EXT, 'a') + \
          '{:s} = {:s}\n'.format(mynotes.config.Config.PRM_INDEX, 'b') + \
          '{:s} = {:s}\n'.format(mynotes.config.Config.PRM_HOME, 'c') + \
          '{:s} = {:s}\n'.format(mynotes.config.Config.PRM_EXCL_FILES, 'd') + \
          '{:s} = {:s}\n'.format(mynotes.config.Config.PRM_EXCL_DIRS, 'e') + \
          '{:s} = {:s}\n'.format(mynotes.config.Config.PRM_PLUGINS_HTML,
                                 'f') + \
          '\n'
    with open(fn, 'w') as fp:
        fp.write(exp)
    return fn


@pytest.mark.parametrize("inp, exp", [
    (None, mynotes.constants.CONFIG_FILE),
    ('a', 'a')
])
def test_Config__init__(inp, exp):
    """Test Config::__init__ function."""
    cfg = mynotes.config.Config(inp)
    assert cfg._file == exp


def test_Config__default_config(empty_file):
    """Test Config class with default config."""
    cfg = mynotes.config.Config(empty_file)
    assert cfg.markdown_ext() == mynotes.constants.MARKDOWN_EXT
    assert cfg.index_file() == mynotes.constants.INDEX_FILE
    assert cfg.home_file() == mynotes.constants.HOME_FILE
    assert cfg.exclude_files() == mynotes.constants.EXCLUDE_FILES
    assert cfg.exclude_dirs() == mynotes.constants.EXCLUDE_DIRS
    assert cfg.plugins_html() == mynotes.constants.PLUGINS_HTML

    exp = '[{:s}]\n'.format(mynotes.constants.PACKAGE_NAME) + \
          '{:s} = {:s}\n'.format(mynotes.config.Config.PRM_MD_EXT,
                                 mynotes.constants.MARKDOWN_EXT) + \
          '{:s} = {:s}\n'.format(mynotes.config.Config.PRM_INDEX,
                                 mynotes.constants.INDEX_FILE) + \
          '{:s} = {:s}\n'.format(mynotes.config.Config.PRM_HOME,
                                 mynotes.constants.HOME_FILE) + \
          '{:s} = {:s}\n'.format(mynotes.config.Config.PRM_EXCL_FILES,
                                 ' '.join(mynotes.constants.EXCLUDE_FILES)) + \
          '{:s} = {:s}\n'.format(mynotes.config.Config.PRM_EXCL_DIRS,
                                 ' '.join(mynotes.constants.EXCLUDE_DIRS)) + \
          '{:s} = {:s}\n'.format(mynotes.config.Config.PRM_PLUGINS_HTML,
                                 ' '.join(mynotes.constants.PLUGINS_HTML)) + \
          '\n'

    with open(empty_file, 'r') as fpr:
        data = fpr.read()
        assert data == exp


def test_Config__edited_config(non_empty_file):
    """Test Config class with default config."""
    cfg = mynotes.config.Config(non_empty_file)
    assert cfg.markdown_ext() == 'a'
    assert cfg.index_file() == 'b'
    assert cfg.home_file() == 'c'
    assert cfg.exclude_files() == ['d']
    assert cfg.exclude_dirs() == ['e']
    assert cfg.plugins_html() == ['f']

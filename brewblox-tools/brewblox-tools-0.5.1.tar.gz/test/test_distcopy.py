"""
Tests dist_copy.py
"""

from unittest.mock import call

import pytest

from brewblox_tools import distcopy

TESTED = distcopy.__name__


@pytest.fixture
def mock_glob(mocker):
    return mocker.patch(TESTED + '.glob.glob')


@pytest.fixture
def mock_path(mocker):
    return mocker.patch(TESTED + '.pathlib.Path')


@pytest.fixture
def mock_copy(mocker):
    return mocker.patch(TESTED + '.shutil.copy')


@pytest.fixture
def mock_remove(mocker):
    return mocker.patch(TESTED + '.os.remove')


def test_distcopy(mock_glob, mock_path, mock_copy, mock_remove):
    mock_glob.return_value = ['f1', 'f2']

    distcopy.main('src dest1 dest2/'.split())

    mock_path.assert_has_calls([
        call('dest1'),
        call().mkdir(parents=True, exist_ok=True),
        call('dest2/'),
        call().mkdir(parents=True, exist_ok=True),
    ])

    mock_remove.assert_has_calls([
        call('f1'),
        call('f2')
    ])

    mock_copy.assert_has_calls([
        call('f1', 'dest1/'),
        call('f2', 'dest1/'),
        call('f1', 'dest2//'),
        call('f2', 'dest2//')
    ])

    mock_glob.assert_has_calls([
        call('dest1/*'),
        call('src/*'),
        call('dest2//*'),
        call('src/*')
    ])

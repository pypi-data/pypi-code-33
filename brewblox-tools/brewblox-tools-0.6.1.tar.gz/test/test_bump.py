"""
Tests bump.py
"""

from subprocess import STDOUT

import pytest

from brewblox_tools import bump

TESTED = bump.__name__


@pytest.fixture
def check_output_mock(mocker):
    m = mocker.patch(TESTED + '.check_output')
    return m


@pytest.fixture
def check_call_mock(mocker):
    m = mocker.patch(TESTED + '.check_call')
    return m


@pytest.fixture
def input_mock(mocker):
    m = mocker.patch('builtins.input')
    return m


@pytest.mark.parametrize('bump_type,new_version', [
    ('major', '4.0.0'),
    ('minor', '3.3.0'),
    ('patch', '3.2.2')
])
def test_bump(check_output_mock, check_call_mock, input_mock, bump_type, new_version):
    check_output_mock.return_value = b'1.2.3\n3.2.1\n'
    input_mock.return_value = 'y'

    bump.main([bump_type])

    check_output_mock.assert_any_call(f'git tag -a {new_version} -m "Version {new_version}"', shell=True)
    check_call_mock.assert_any_call('git push --tags', shell=True, stderr=STDOUT)
    assert input_mock.call_count == 2


def test_bump_no_push(check_output_mock, input_mock, check_call_mock):
    check_output_mock.return_value = b'1.2.3\n3.2.1\n'
    input_mock.side_effect = ['y', 'n']

    bump.main(['minor'])

    check_output_mock.assert_any_call(f'git tag -a 3.3.0 -m "Version 3.3.0"', shell=True)
    assert input_mock.call_count == 2
    assert check_call_mock.call_count == 0


def test_bump_nok(check_output_mock, input_mock):
    check_output_mock.return_value = b'1.2.3\n3.2.1\n'
    input_mock.return_value = 'n'

    bump.main(['minor'])
    assert check_output_mock.call_count == 1


@pytest.mark.parametrize('user_input,expected', [
    (['y'], True),
    (['n'], False),
    (['Y'], True),
    (['N'], False),
    (['Yes'], True),
    (['No'], False),
    (['y', 'n'], True),
    (['n', 'y'], False),
    (['maybe', 'y'], True),
    (['maybe', 'I think so...', 'n'], False),
    ([''], True),
])
def test_user_yes_no_query(input_mock, user_input, expected):
    input_mock.side_effect = user_input
    assert bump.user_yes_no_query('Are you sure?') == expected

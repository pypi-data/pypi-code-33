import subprocess
import unittest

import mock
import pytest

from oc_wrapper.policy import Policy


class TestPolicy(unittest.TestCase):
    def test_add_role_to_group(self):
        with mock.patch('subprocess.check_call') as mock_call:
            Policy(True).add_role_to_group('foo', 'bar', 'baz')
            mock_call.assert_called_once_with(['oc', 'policy', 'add-role-to-group', 'foo', 'bar', '-n', 'baz'],
                                              stderr=subprocess.STDOUT)

        with mock.patch('os.system') as mock_call:
            Policy(False).add_role_to_group('foo', 'bar', 'baz')
            mock_call.assert_called_once_with('oc policy add-role-to-group foo bar -n baz')


if __name__ == '__main__':
    pytest.main()

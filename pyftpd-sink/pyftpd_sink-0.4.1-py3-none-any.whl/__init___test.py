# pylint: disable=missing-docstring

import unittest.mock

import pytest

import pyftpd_sink


@pytest.mark.parametrize(('env', 'argv', 'expected_umask'), [
    ({}, [], None),
    ({}, ['--umask', str(0o0027)], 0o0027),
    ({}, ['--umask', str(0o0177)], 0o0177),
    ({}, ['--umask', '23'], 0o0027),
    ({}, ['--umask', '127'], 0o0177),
    ({'UMASK': str(0o0022)}, [], 0o0022),
    ({'UMASK': str(0o0022)}, ['--umask', str(0o0027)], 0o0027),
])
def test_main_umask(env, argv, expected_umask):
    with unittest.mock.patch('pyftpd_sink.serve') as serve_mock:
        with unittest.mock.patch('sys.argv', ['', '--user', 'u', '--pwd-hash', 'p'] + argv):
            with unittest.mock.patch('os.environ', env):
                pyftpd_sink.main()
    serve_mock.assert_called_once()
    serve_kwargs = serve_mock.call_args[1]
    assert expected_umask == serve_kwargs['umask']

import unittest
import sys

try:
    import unittest.mock as mock
except ImportError:
    import mock

import LbScriptsLegacy


class TestUtils(unittest.TestCase):

    @mock.patch('LbScriptsLegacy.os')
    def test_gen_wrapper(self, mock_os):
        """ Testing that the mapping is done correctly """
        wrapper = LbScriptsLegacy.gen_wrapper('testMethod', 'test_method')
        args = ['testMethod', 'arg1', 'arg2', 'arg3']
        sys.argv = args
        wrapper()
        expected_args = ['test_method', ['test_method'] + args[1:]]
        mock_os.execvp.assert_called_once_with(*expected_args)


if __name__ == '__main__':
    unittest.main()

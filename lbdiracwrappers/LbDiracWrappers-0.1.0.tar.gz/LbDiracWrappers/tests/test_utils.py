import unittest
import sys

try:
    import unittest.mock as mock
except ImportError:
    import mock

from LbDiracWrappers import lhcb_proxy_init, lhcb_proxy_info

class TestUtils(unittest.TestCase):

    @mock.patch('LbDiracWrappers.os')
    def test_lhcb_proxy_init(self, mock_os):
        sys.argv = []
        lhcb_proxy_init()
        expected_args = ['lb-run', ['lb-run', '-c', 'best', 'LHCbDirac/prod', 'lhcb-proxy-init']]
        mock_os.execvp.assert_called_once_with(*expected_args)

    @mock.patch('LbDiracWrappers.os')
    def test_lhcb_proxy_info(self, mock_os):
        sys.argv = []
        lhcb_proxy_info()
        expected_args = ['lb-run', ['lb-run', '-c', 'best', 'LHCbDirac/prod', 'dirac-proxy-info']]
        mock_os.execvp.assert_called_once_with(*expected_args)



if __name__ == '__main__':
    unittest.main()

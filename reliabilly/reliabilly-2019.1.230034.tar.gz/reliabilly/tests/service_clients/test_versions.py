from unittest import TestCase, skipUnless
from unittest.mock import MagicMock
from requests.exceptions import RequestException
from reliabilly.components.tools.version import check_versions, get_service_versions, version, \
    run_version_check, check_version_list
from reliabilly.settings import Settings, Constants


LOCAL_TARGET = 'http://localhost:8080'
LOCAL_DEV_VERSION = 'dev'
SERVICE_LIST = ['portfolios', 'infrastructure']
SERVICE_VERSION_LIST = {'portfolios': LOCAL_DEV_VERSION, 'infrastructure': LOCAL_DEV_VERSION}
TEST_PAYLOAD = '{"service": "infrastructure", "version": "dev", "build-number": "None"}'


class VersionCheckTests(TestCase):
    def test_check_service_versions(self):
        mock = MagicMock()
        mock_result = MagicMock()
        mock_result.text = TEST_PAYLOAD
        mock.get.return_value = mock_result
        result = get_service_versions(Constants.DUMMY, SERVICE_LIST, mock)
        self.assertEqual(len(result), 2)

    def test_check_service_fail(self):
        mock = MagicMock()
        mock.get.side_effect = RequestException
        result = get_service_versions(Constants.DUMMY, SERVICE_LIST, mock)
        self.assertIsNotNone(result)

    def test_check_service_404(self):
        mock = MagicMock()
        mock_result = MagicMock()
        mock_result.return_code = 404
        mock.get.side_effect = mock_result
        result = get_service_versions(Constants.DUMMY, SERVICE_LIST, mock)
        self.assertIsNotNone(result)

    def test_run_version_check(self):
        mock = MagicMock()
        mock_result = MagicMock()
        mock_result.status_code = 200
        mock_result.text = TEST_PAYLOAD
        mock.get.side_effect = RequestException
        result = run_version_check(Constants.DUMMY, Constants.DUMMY, SERVICE_LIST, mock)
        self.assertFalse(result)
        mock.reset_mock()
        mock.get.side_effect = [mock_result, mock_result]
        result = run_version_check(Constants.DUMMY, LOCAL_DEV_VERSION, SERVICE_LIST, mock)
        self.assertTrue(result)

    def test_check_version_success(self):
        mock = MagicMock()
        mock.return_value = True
        result = check_versions(Constants.DUMMY, LOCAL_DEV_VERSION, SERVICE_LIST, 1, mock)
        self.assertTrue(result)

    def test_retry_logic(self):
        mock = MagicMock()
        mock.side_effect = [False, False, False, True]
        result = check_versions(Constants.DUMMY, LOCAL_DEV_VERSION, SERVICE_LIST, 1, mock, .1)
        self.assertTrue(result)
        self.assertEqual(mock.call_count, 4)

    def test_check_version_list(self):
        mock = MagicMock()
        mock.return_value = True
        result = check_version_list(SERVICE_VERSION_LIST, LOCAL_DEV_VERSION)
        self.assertTrue(result)

    def test_version(self):
        self.assertIsNotNone(version())

    @skipUnless(Settings.RUN_SKIPPED, Constants.RUN_SKIPPED_MSG)
    def test_real_version_check(self):
        result = check_versions(LOCAL_TARGET, LOCAL_DEV_VERSION, SERVICE_LIST, 1)
        self.assertTrue(result)

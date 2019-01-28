import quackdns.updater as core
import sys
import unittest

__TEST_TOKEN__ = "b10eae0b-4153-41cc-8be1-1c811de51c0d"
__TEST_DOMAIN__ = "test-quackdns"


class MockUpdaterTest(unittest.TestCase):
    def test_mock_updater(self):
        """
        Check that the mock implementation adheres to the contract
        defined in AbstractUpdater.

        :return:
        """
        mock_updater = core.MockUpdater()
        success_response = "Updated!"

        self.assertEqual(mock_updater.update(), success_response)


class UpdaterTest(unittest.TestCase):
    def test_updater(self):
        updater = core.Updater(token=__TEST_TOKEN__, domains=__TEST_DOMAIN__)

        e = None
        response = ""
        try:
            response = updater.update()
        except:
            e = sys.exc_info()[0]
        self.assertIsNone(e)
        self.assertIsNot(response, "")


if __name__ == '__main__':
    unittest.main()

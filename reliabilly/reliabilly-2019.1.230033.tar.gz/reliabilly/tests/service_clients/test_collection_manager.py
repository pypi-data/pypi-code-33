from unittest import TestCase, skipUnless
from unittest.mock import MagicMock
from reliabilly.components.collection.collection_manager import CollectionManager
from reliabilly.settings import Constants, Settings


class CollectionManagerTests(TestCase):
    def test_collection_manager(self):
        mock = MagicMock()
        manager = CollectionManager(client=mock)
        new_key = manager.collection_started('dummy')
        self.assertIsNotNone(new_key)
        self.assertTrue(manager.collection_completed(new_key, True))
        self.assertTrue(manager.collection_completed(new_key, False))
        status = manager.get_collection_status(new_key)
        self.assertIsNotNone(status)
        mock.find.return_value = {Constants.COLLECTION_STATUS_KEY: Constants.COLLECTION_STARTED_STATUS}
        self.assertTrue(manager.is_collection_running('dummy'))
        mock.find.return_value = {Constants.DB_ID_KEY: 'dummy',
                                  Constants.COLLECTION_STATUS_KEY: Constants.COLLECTION_FAILED_STATUS}
        self.assertFalse(manager.is_collection_running('dummy'))
        mock.find.return_value = None
        status = manager.get_collection_status(new_key)
        self.assertIsNone(status)
        self.assertFalse(manager.is_collection_running('dummy'))

    @skipUnless(Settings.RUN_SKIPPED, Constants.RUN_SKIPPED_MSG)
    def test_real_manager(self):
        test_collector = 'test_collector'
        manager = CollectionManager()
        manager.purge_prior_collections()
        self.assertIsNone(manager.get_collection_status(test_collector))
        self.assertFalse(manager.is_collection_running(test_collector))
        self.assertTrue(manager.collection_started(test_collector))
        self.assertTrue(manager.is_collection_running(test_collector))
        result = manager.get_collection_status(test_collector)
        self.assertEqual(result[Constants.COLLECTION_STATUS_KEY], Constants.COLLECTION_STARTED_STATUS)
        self.assertTrue(manager.collection_completed(test_collector, True))
        result = manager.get_collection_status(test_collector)
        self.assertEqual(result[Constants.COLLECTION_STATUS_KEY], Constants.COLLECTION_SUCCESS_STATUS)
        self.assertFalse(manager.is_collection_running(test_collector))
        self.assertTrue(manager.collection_started(test_collector))
        self.assertTrue(manager.collection_completed(test_collector))
        self.assertFalse(manager.is_collection_running(test_collector))
        self.assertIsNone(manager.get_collection_status(test_collector))

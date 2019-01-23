# pylint: disable=no-self-use
from unittest import TestCase
from unittest.mock import MagicMock
from reliabilly.components.data.mongo_client import MongoDataClient


class TestMongoDataClient(TestCase):
    def test_real_constructor(self):
        self.assertIsNotNone(MongoDataClient())

    def test_rename_table(self):
        client_mock = MagicMock()
        db_mock = MagicMock()
        collection_mock = MagicMock()
        client_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock
        data_client = MongoDataClient(client=client_mock)
        data_client.rename_table(None, 'new_name')
        collection_mock.rename.assert_called_with('new_name', dropTarget=True)

    def test_table_exists(self):
        client_mock = MagicMock()
        db_mock = MagicMock()
        db_mock.collection_names.return_value = ['table_name']
        collection_mock = MagicMock()
        client_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock
        data_client = MongoDataClient(client=client_mock)
        result = data_client.table_exists('table_name')
        self.assertTrue(result)

    def test_create_true(self):
        client_mock = MagicMock()
        db_mock = MagicMock()
        collection_mock = MagicMock()
        client_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock
        data_client = MongoDataClient(client=client_mock)
        mock_result = MagicMock()
        mock_result.inserted_id = True
        collection_mock.insert_one.return_value = mock_result
        res = data_client.create(None)
        self.assertTrue(res)

    def test_restore_true(self):
        client_mock = MagicMock()
        db_mock = MagicMock()
        collection_mock = MagicMock()
        client_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock
        data_client = MongoDataClient(client=client_mock)
        mock_result = MagicMock()
        mock_result.inserted_id = True
        collection_mock.insert_many.return_value = mock_result
        res = data_client.restore(None)
        self.assertTrue(res)

    def test_create_false(self):
        client_mock = MagicMock()
        db_mock = MagicMock()
        collection_mock = MagicMock()
        mock_result = MagicMock()
        collection_mock.insert_one.return_value = mock_result
        mock_result.inserted_id = None
        client_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock
        data_client = MongoDataClient(client=client_mock)
        res = data_client.create(None)
        self.assertFalse(res)

    def test_get(self):
        client_mock = MagicMock()
        db_mock = MagicMock()
        collection_mock = MagicMock()
        collection_mock.find_one.return_value = True
        client_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock
        data_client = MongoDataClient(client=client_mock)
        result = data_client.get(None)
        self.assertEqual(result, True)

    def test_delete(self):
        client_mock = MagicMock()
        db_mock = MagicMock()
        collection_mock = MagicMock()
        client_mock.deleted_count = 1
        collection_mock.delete_one.return_value = client_mock
        client_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock
        data_client = MongoDataClient(client=client_mock)
        result = data_client.delete(None)
        self.assertEqual(result, True)

    def test_get_specific(self):
        client_mock = MagicMock()
        db_mock = MagicMock()
        collection_mock = MagicMock()
        collection_mock.find_one.return_value = True
        client_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock
        data_client = MongoDataClient(client=client_mock)
        result = data_client.get_specific(None, db_mock)
        self.assertEqual(result, True)

    def test_find(self):
        client_mock = MagicMock()
        db_mock = MagicMock()
        collection_mock = MagicMock()
        collection_mock.find_one.return_value = True
        client_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock
        data_client = MongoDataClient(client=client_mock)
        result = data_client.find(None, db_mock)
        self.assertEqual(result, True)

    def test_update(self):
        client_mock = MagicMock()
        db_mock = MagicMock()
        collection_mock = MagicMock()
        collection_mock.find_one_and_replace.return_value = True
        client_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock
        data_client = MongoDataClient(client=client_mock)
        result = data_client.update(None, db_mock)
        self.assertEqual(result, True)

    def test_get_all(self):
        client_mock = MagicMock()
        db_mock = MagicMock()
        collection_mock = MagicMock()
        collection_mock.find.return_value = []
        client_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock
        data_client = MongoDataClient(client=client_mock)
        result = data_client.get_all()
        self.assertEqual(result, [])

    def test_read(self):
        client_mock = MagicMock()
        db_mock = MagicMock()
        collection_mock = MagicMock()
        mock = MagicMock()
        mock.limit.return_value = [{'item': 'item_name'}]
        mock.skip.return_value = mock
        mock.count.return_value = 5
        collection_mock.find.return_value = mock
        client_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock
        data_client = MongoDataClient(client=client_mock)
        result = data_client.read(2, 10, {'name': 'item'})
        self.assertEqual(result, ([{'item': 'item_name'}], 2, 10, 5))

    def test_delete_db(self):
        client_mock = MagicMock()
        client_mock.drop_database.return_value = True
        data_client = MongoDataClient(client=client_mock)
        data_client.delete_db()
        client_mock.drop_database.assert_called()

    def test_count(self):
        client_mock = MagicMock()
        db_mock = MagicMock()
        count_mock = MagicMock()
        count_mock.count.return_value = 10
        collection_mock = MagicMock()
        collection_mock.find.return_value = count_mock
        client_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock
        data_client = MongoDataClient(client=client_mock)
        count = data_client.count()
        self.assertEqual(count, 10)

    def test_purge(self):
        client_mock = MagicMock()
        db_mock = MagicMock()
        collection_mock = MagicMock()
        collection_mock.drop.return_value = True
        client_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock
        data_client = MongoDataClient(client=client_mock)
        purge = data_client.purge()
        self.assertEqual(purge, True)

    def test_dependency(self):
        mock = MagicMock()
        data_client = MongoDataClient(client=mock)
        self.assertEqual(data_client, data_client.get_dependency(mock))

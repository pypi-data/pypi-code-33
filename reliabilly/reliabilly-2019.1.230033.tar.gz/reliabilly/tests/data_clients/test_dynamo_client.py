import warnings
from unittest import TestCase
from unittest.mock import MagicMock

from reliabilly.components.data.dynamo_client import DynamoDataClient
from reliabilly.components.models.base import BaseModel
from reliabilly.settings import Constants


TEST_KEY = 'test_key'
TEST_VALUE = 'test_value'
SAMPLE_ITEMS = [{TEST_KEY: TEST_VALUE}]
SAMPLE_ITEMS_RESPONSE = {Constants.DYNAMO_ITEMS_KEY: SAMPLE_ITEMS, Constants.DYNAMO_COUNT_KEY: len(SAMPLE_ITEMS)}
SAMPLE_RESPONSE_SUCCESS = {
    Constants.DYNAMO_RESPONSE_METADATA: {Constants.DYNAMO_SUCCESS_STATUS: Constants.SUCCESS_RESPONSE_CODE}}
SAMPLE_RESPONSE_FAIL = {
    Constants.DYNAMO_RESPONSE_METADATA: {Constants.DYNAMO_SUCCESS_STATUS: Constants.UNAUTHORIZED_CODE}}


class TestDynamoDataClient(TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning)

    @staticmethod
    def get_mocked_client(mock):
        mock.Table.return_value = mock
        return DynamoDataClient(factory=mock, table_name=Constants.EMPTY, client=mock, resource=mock)

    def test_instantiation(self):
        mock = MagicMock()
        dynamo = DynamoDataClient(factory=mock, table_name=Constants.EMPTY)
        self.assertIsNotNone(dynamo)

    def test_get(self):
        client_mock = MagicMock()
        dynamo = self.get_mocked_client(client_mock)
        self.assertTrue(dynamo.get(Constants.EMPTY))

    def test_get_specific(self):
        client_mock = MagicMock()
        dynamo = self.get_mocked_client(client_mock)
        self.assertTrue(dynamo.get_specific(Constants.EMPTY, Constants.EMPTY))

    def test_create_true(self):
        client_mock = MagicMock()
        client_mock.put_item.return_value = SAMPLE_RESPONSE_SUCCESS
        dynamo = self.get_mocked_client(client_mock)
        self.assertIsNotNone(dynamo)
        result = dynamo.create(BaseModel())
        self.assertTrue(result)

    def test_get_all(self):
        client_mock = MagicMock()
        dynamo = self.get_mocked_client(client_mock)
        self.assertTrue(dynamo.get_all())

    def test_rename_table(self):
        client_mock = MagicMock()
        self.assertIsNotNone(client_mock)

    def test_create_false(self):
        client_mock = MagicMock()
        self.assertIsNotNone(client_mock)

    def test_delete(self):
        client_mock = MagicMock()
        client_mock.delete_item.return_value = SAMPLE_RESPONSE_SUCCESS
        dynamo = self.get_mocked_client(client_mock)
        self.assertTrue(dynamo.delete(TEST_VALUE))

    def test_delete_table(self):
        client_mock = MagicMock()
        client_mock.delete_table.return_value = SAMPLE_RESPONSE_SUCCESS
        dynamo = self.get_mocked_client(client_mock)
        self.assertTrue(dynamo.delete_table(TEST_VALUE))

    def test_find(self):
        client_mock = MagicMock()
        client_mock.scan.return_value = SAMPLE_ITEMS_RESPONSE
        dynamo = self.get_mocked_client(client_mock)
        self.assertEqual(len(dynamo.find(TEST_KEY, TEST_VALUE)), len(SAMPLE_ITEMS))
        self.assertEqual(dynamo.count(), len(SAMPLE_ITEMS))

    def test_update(self):
        client_mock = MagicMock()
        self.assertIsNotNone(client_mock)

    def test_read(self):
        client_mock = MagicMock()
        self.assertIsNotNone(client_mock)

    def test_delete_db(self):
        client_mock = MagicMock()
        client_mock.delete_table.return_value = SAMPLE_RESPONSE_SUCCESS
        dynamo = self.get_mocked_client(client_mock)
        self.assertTrue(dynamo.delete_db())

    def test_purge(self):
        client_mock = MagicMock()
        client_mock.scan.return_value = SAMPLE_ITEMS_RESPONSE
        client_mock.delete_item.return_value = SAMPLE_RESPONSE_SUCCESS
        dynamo = self.get_mocked_client(client_mock)
        self.assertTrue(dynamo.purge())

    def test_find_items(self):
        mock = MagicMock()
        client = DynamoDataClient(factory=mock, table_name=Constants.EMPTY, client=mock, resource=mock)
        items = [{'id': 111, 'test1': 'value1', 'test2': 'value1', 'test3': 1},
                 {'id': 222, 'test1': 'value2', 'test2': 'value1', 'test3': 2},
                 {'id': 333, 'test1': 'value3', 'test2': 'value1', 'test3': 3},
                 {'id': 444, 'test1': 'value4', 'test2': 'value1', 'test3': 4}]
        result, *_ = client.find_items_in_list(items, 0, 5, **{'test1': 'value1', 'test3': 1})
        self.assertEqual(len(result), 1)
        result, *_ = client.find_items_in_list(items, 0, 5, **{'test2': 'value1', 'test3': 1})
        self.assertEqual(len(result), 1)
        result, *_ = client.find_items_in_list(items, 0, 5, **{'test2': 'value1'})
        self.assertEqual(len(result), 4)
        result, *_ = client.find_items_in_list(items, 0, 5, **{'test2': 'value1', 'test3': '4'})
        self.assertEqual(len(result), 1)
        result, *_ = client.find_items_in_list(items, 0, 5, **{'test2': 'value2'})
        self.assertEqual(len(result), 0)

    def test_filter(self):
        mock = MagicMock()
        client = DynamoDataClient(factory=mock, table_name=Constants.EMPTY, client=mock, resource=mock)
        items = [{'id': 111, 'test1': 'value1', 'test2': 'value1', 'test3': 1},
                 {'id': 222, 'test1': 'value2', 'test2': 'value1', 'test3': 2},
                 {'id': 333, 'test1': 'value3', 'test2': 'value1', 'test3': 3},
                 {'id': 444, 'test1': 'value4', 'test2': 'value1', 'test3': 4}]
        mock.Table.return_value = mock
        mock.scan.return_value = {Constants.DYNAMO_ITEMS_KEY: items}
        result, *_ = client.filter()
        self.assertEqual(len(result), len(items))

    def test_get_converted_model(self):
        mock = MagicMock()
        client = DynamoDataClient(factory=mock, table_name=Constants.EMPTY, client=mock, resource=mock)
        model = {'name': 'name', 'portfolio': '', 'test': 1.0, 'dict': {'test': ''}}
        converted_model = client.get_converted_model(model)
        self.assertTrue('portfolio' not in converted_model.keys())
        self.assertTrue('dict' not in converted_model.keys())
        self.assertTrue('name' in converted_model.keys())
        self.assertTrue('test' in converted_model.keys())

    def test_dependency(self):
        mock = MagicMock()
        data_client = DynamoDataClient(factory=mock, client=mock)
        self.assertEqual(data_client, data_client.get_dependency(mock))

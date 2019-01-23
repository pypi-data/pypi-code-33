# pylint: skip-file
import json
import logging
import unittest
from unittest.mock import MagicMock
from reliabilly.components.controllers.data_handler import DataHandler
from reliabilly.settings import Constants


class TestDataHandler(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def test_get_single_with_no_item_returns_RESOURCE_NOT_FOUND(self):
        # Setup
        mock_client = MagicMock()
        mock_id = MagicMock()
        mock_client.get.return_value = None
        data_handler = DataHandler(mock_client)

        # Execute
        result = data_handler.handle_get_request_single(mock_id)

        # Assert
        self.assertEqual(result[0], Constants.RESOURCE_NOT_FOUND_CODE)
        self.assertEqual(result[1], Constants.RESOURCE_NOT_FOUND_MESSAGE)

    def test_get_single_with_item_returns_SUCCESS_RESPONSE_CODE(self):
        # Setup
        mock_id = MagicMock()
        mock_data_client = MagicMock()
        item = [{'name': 'item'}]
        mock_data_client.get.return_value = item
        data_handler = DataHandler(mock_data_client)

        # Execute
        result = data_handler.handle_get_request_single(mock_id)

        # Assert
        self.assertEqual(result[0], Constants.SUCCESS_RESPONSE_CODE)
        self.assertEqual(result[1], json.dumps(item))

    def test_get_with_item_returns_SUCCESS_RESPONSE_CODE(self):
        # Setup
        mock_request = MagicMock()
        mock_data_client = MagicMock()
        items = [{'name1': 'item1'}, {'name2': 'item2'}]
        mock_data_client.count.return_value = 2
        mock_data_client.filter.return_value = [items, 0, 25, 2]
        data_handler = DataHandler(mock_data_client)

        # Execute
        mock_request.args = dict()
        result = data_handler.handle_get_request(mock_request)
        # Assert
        self.assertEqual(result[0], Constants.SUCCESS_RESPONSE_CODE)
        result_data = json.loads(result[1])
        self.assertEqual(result_data[list(result_data)[0]], items)

    def test_get_with_item_returns_BAD_REQUEST_CODE(self):
        # Setup
        mock_request = MagicMock()
        mock_data_client = MagicMock()
        mock_data_client.read.return_value = ValueError
        data_handler = DataHandler(mock_data_client)

        # Execute
        mock_request.args = dict()
        result = data_handler.handle_get_request(mock_request)

        # Assert
        self.assertEqual(result[0], Constants.BAD_REQUEST_CODE)
        self.assertEqual(result[1], Constants.BAD_REQUEST_MESSAGE)

    def test_get_with_negative_limit_returns_BAD_REQUEST_CODE(self):
        # Setup
        mock_request = MagicMock()
        mock_data_client = MagicMock()
        mock_data_client.filter.return_value = ("mock_items", "mock_offset",
                                                -1, "mock_count")
        data_handler = DataHandler(mock_data_client)

        # Execute
        result = data_handler.handle_get_request(mock_request)

        # Assert
        self.assertEqual(result[0], Constants.BAD_REQUEST_CODE)
        self.assertEqual(result[1], Constants.BAD_REQUEST_MESSAGE)

    def test_post_with_bad_request_returns_BAD_REQUEST(self):
        # Setup
        mock_data_client = MagicMock()
        data_handler = DataHandler(mock_data_client)

        # Execute
        result = data_handler.handle_post_request(None)

        # Assert
        self.assertEqual(result[0], Constants.BAD_REQUEST_CODE)
        self.assertEqual(result[1], Constants.BAD_REQUEST_MESSAGE)

    def test_post_with_failure_returns_error(self):
        # Setup
        mock_data_client = MagicMock()
        mock_data_client.create.return_value = False
        payload = {'name': 'item'}
        data_handler = DataHandler(mock_data_client)

        # Execute
        result = data_handler.handle_post_request(payload)

        # Assert
        self.assertEqual(result, "Failed to create new item: {'name': 'item'}")

    def test_post_with_request_returns_CREATED_SUCCESS(self):
        # Setup
        mock_model = MagicMock()
        mock_data_client = MagicMock()
        payload = {'name': 'item'}
        mock_model.add.return_value = payload
        data_handler = DataHandler(mock_data_client)

        # Execute
        result = data_handler.handle_post_request(payload)

        # Assert
        self.assertEqual(result[0], Constants.CREATED_SUCCESS_CODE)
        self.assertEqual(result[1], json.dumps(payload))

    def test_count_returns_SUCCESS_RESPONSE(self):
        # Setup
        mock_data_client = MagicMock()
        mock_data_client.count.return_value = 10
        data_handler = DataHandler(mock_data_client)

        # Execute
        result = data_handler.handle_count_request()

        # Assert
        self.assertEqual(result[0], Constants.SUCCESS_RESPONSE_CODE)
        self.assertEqual(result[1], json.dumps(10))

    def test_purge_returns_SUCCESS_RESPONSE(self):
        # Setup
        mock_data_client = MagicMock()
        purge_message = {'message': 'Purge Successful!'}
        mock_data_client.purge.return_value = purge_message
        data_handler = DataHandler(mock_data_client)

        # Execute
        result = data_handler.handle_purge_request()

        # Assert
        self.assertEqual(result[0], Constants.SUCCESS_RESPONSE_CODE)
        self.assertEqual(result[1], json.dumps(purge_message))

    def test_delete_returns_SUCCESS_RESPONSE(self):
        # Setup
        mock_data_client = MagicMock()
        mock_data_client.delete.return_value = True
        data_handler = DataHandler(mock_data_client)

        # Execute
        result = data_handler.handle_delete_request(mock_data_client)

        # Assert
        self.assertEqual(result[0], Constants.SUCCESS_RESPONSE_CODE)
        self.assertEqual(result[1], Constants.DELETE_REQUEST_MESSAGE)

    def test_delete_returns_RESOURCE_NOT_FOUND_CODE(self):
        # Setup
        mock_data_client = MagicMock()
        mock_data_client.delete.return_value = False
        data_handler = DataHandler(mock_data_client)

        # Execute
        result = data_handler.handle_delete_request(mock_data_client)

        # Assert
        self.assertEqual(result[0], Constants.RESOURCE_NOT_FOUND_CODE)
        self.assertEqual(result[1], Constants.RESOURCE_NOT_FOUND_MESSAGE)

    def test_update_returns_SUCCESS_RESPONSE(self):
        # Setup
        mock_data_client = MagicMock()
        mock_data_client.delete.return_value = True
        mock_data_client.create.return_value = True
        data_handler = DataHandler(mock_data_client)

        # Execute
        result = data_handler.handle_update_request(
            mock_data_client, mock_data_client)

        # Assert
        self.assertEqual(result[0], Constants.CREATED_SUCCESS_CODE)

    def test_update_returns_RESOURCE_NOT_FOUND_CODE(self):
        # Setup
        mock_data_client = MagicMock()
        mock_data_client.delete.return_value = False
        data_handler = DataHandler(mock_data_client)

        # Execute
        result = data_handler.handle_update_request(
            mock_data_client, mock_data_client)

        # Assert
        self.assertEqual(result[0], Constants.RESOURCE_NOT_FOUND_CODE)
        self.assertEqual(result[1], Constants.RESOURCE_NOT_FOUND_MESSAGE)

    def test_update_returns_BAD_REQUEST_CODE(self):
        # Setup
        mock_data_client = MagicMock()
        data_handler = DataHandler(mock_data_client)

        # Execute
        result = data_handler.handle_update_request(
            mock_data_client, None)

        # Assert
        self.assertEqual(result[0], Constants.BAD_REQUEST_CODE)
        self.assertEqual(result[1], Constants.BAD_REQUEST_MESSAGE)

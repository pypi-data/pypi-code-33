import json
from collections import OrderedDict
from reliabilly.components.logger import Logger, log_exception
from reliabilly.settings import Constants, Settings


class DataHandler:

    def __init__(self, data_client):
        self.data_client = data_client
        self.logger = Logger()

    @log_exception
    def handle_get_request_single(self, item_id):
        item = self.data_client.get(item_id)
        if item:
            return Constants.SUCCESS_RESPONSE_CODE, self.to_json(item)
        return Constants.RESOURCE_NOT_FOUND_CODE, Constants.RESOURCE_NOT_FOUND_MESSAGE

    def handle_get_request(self, request=None):
        try:
            result = []
            items, offset, limit, count = self.get_filtered_data(request)
            for item in items:
                result.append(item)
            data = OrderedDict()
            data[Settings.SERVICE_NAME] = result
            data['offset'] = offset
            data['limit'] = limit
            data['total'] = count

            if limit & limit < 0:
                raise ValueError
            return Constants.SUCCESS_RESPONSE_CODE, self.to_json(data)
        # pylint: disable=broad-except
        except(ValueError, Exception) as ex:
            self.logger.error(f'Error in general handle_get_request ex: {ex}', exc_info=True)
            return Constants.BAD_REQUEST_CODE, Constants.BAD_REQUEST_MESSAGE

    def get_filtered_data(self, request):
        if request:
            return self.data_client.filter(**request.args)
        return self.data_client.filter()

    @log_exception
    def handle_post_request(self, payload):
        if payload is None:
            return Constants.BAD_REQUEST_CODE, Constants.BAD_REQUEST_MESSAGE
        if self.data_client.create(payload):
            return Constants.CREATED_SUCCESS_CODE, self.to_json(payload)
        error = "Failed to create new item: {}".format(payload)
        return error

    @log_exception
    def handle_restore_request(self, payload):
        if payload is None:
            return Constants.BAD_REQUEST_CODE, Constants.BAD_REQUEST_MESSAGE
        if self.data_client.restore(payload):
            return Constants.CREATED_SUCCESS_CODE, self.to_json(payload)
        error = "Failed to restore items: {}".format(payload)
        return error

    @log_exception
    def handle_count_request(self):
        return Constants.SUCCESS_RESPONSE_CODE, self.to_json(self.data_client.count())

    @log_exception
    def handle_purge_request(self):
        self.data_client.purge()
        return Constants.SUCCESS_RESPONSE_CODE, Constants.PURGE_REQUEST_MESSAGE

    @log_exception
    def handle_delete_request(self, item_id):
        result = self.data_client.delete(item_id)
        if result:
            return Constants.SUCCESS_RESPONSE_CODE, Constants.DELETE_REQUEST_MESSAGE
        return Constants.RESOURCE_NOT_FOUND_CODE, Constants.RESOURCE_NOT_FOUND_MESSAGE

    @log_exception
    def handle_update_request(self, item_id, payload):
        if payload is None:
            return Constants.BAD_REQUEST_CODE, Constants.BAD_REQUEST_MESSAGE
        if self.data_client.delete(item_id):
            return self.handle_post_request(payload)
        return Constants.RESOURCE_NOT_FOUND_CODE, Constants.RESOURCE_NOT_FOUND_MESSAGE

    @staticmethod
    @log_exception
    def to_json(model):
        return json.dumps(model, default=str)

import json
from threading import Thread

from reliabilly.components.controllers.data_controller import DataController, http, get_route, get_item_route, \
    get_log_string
from reliabilly.components.logger import Logger
from reliabilly.components.monitoring import MonitoringProvider
from reliabilly.settings import Settings, Constants


def perform_collection(collector):
    return collector.perform_collection()


class CollectionController:
    name = Settings.SERVICE_NAME
    monitor = MonitoringProvider()

    def __init__(self, **kwargs):
        self.logger = Logger()
        self.collector = kwargs.get(Constants.COLLECTOR, None)
        self.controller = kwargs.get(Constants.CONTROLLER, DataController(**kwargs))
        self.client = kwargs.get(Constants.CLIENT, None)

    @http(Constants.GET_REQUEST, get_route(Constants.PING_ROUTE))
    def ping(self, request):
        return self.controller.ping(request)

    @http(Constants.OPTIONS_REQUEST, get_route())
    @http(Constants.OPTIONS_REQUEST, get_route(Constants.RUN_ROUTE))
    def options(self, request):
        return self.controller.options(request)

    @http(Constants.OPTIONS_REQUEST, get_item_route())
    def options_item(self, request, item_id):
        return self.controller.options_item(request, item_id)

    @http(Constants.GET_REQUEST, get_route())
    def get(self, request):
        return self.controller.get(request)

    @http(Constants.POST_REQUEST, get_route(Constants.PURGE_ROUTE))
    def purge(self, request):
        return self.controller.purge(request)

    @http(Constants.GET_REQUEST, get_item_route())
    def get_one(self, request, item_id):
        return self.controller.get_one(request, item_id)

    @http(Constants.GET_REQUEST, get_route(Constants.COUNT_ROUTE))
    def count(self, request):
        return self.controller.count(request)

    @http(Constants.GET_REQUEST, get_route(Constants.HEALTH_ROUTE))
    def health(self, request):
        return self.controller.health(request)

    @http(Constants.GET_REQUEST, get_route(Constants.VERSION_ROUTE))
    def version(self, request):
        return self.controller.version(request)

    @http(Constants.PUT_REQUEST, get_route())
    @http(Constants.DELETE_REQUEST, get_route())
    def bad_verbs(self, request):
        return self.controller.bad_verbs(request)

    @http(Constants.POST_REQUEST, get_route())
    def post(self, request):
        self.logger.info(get_log_string(request, Constants.POST_REQUEST, self.name))
        return Constants.BAD_REQUEST_CODE, Constants.BAD_REQUEST_MESSAGE

    @http(Constants.PUT_REQUEST, get_item_route())
    def put(self, request, item_id):
        self.logger.info(get_log_string(request, Constants.PUT_REQUEST, self.name, item_id))
        return Constants.BAD_REQUEST_CODE, Constants.BAD_REQUEST_MESSAGE

    @http(Constants.POST_REQUEST, get_route(Constants.COLLECTION_ROUTE))
    def collect(self, request):
        return self.collect_post(request, self.collector, self.logger)

    @http(Constants.GET_REQUEST, get_route(Constants.COLLECTION_ROUTE))
    def collect_result(self, request):
        return self.collect_get(request, self.collector, self.logger)

    @http(Constants.DELETE_REQUEST, get_route(Constants.COLLECTION_ROUTE))
    def collect_purge(self, request):
        return self.collect_delete(request, self.collector, self.logger)

    @http(Constants.DELETE_REQUEST, get_item_route())
    def delete(self, request, item_id):
        self.logger.info(get_log_string(request, Constants.DELETE_REQUEST, self.name, item_id))
        return Constants.BAD_REQUEST_CODE, Constants.BAD_REQUEST_MESSAGE

    @staticmethod
    def collect_post(request, collector, logger):
        logger.info(get_log_string(request, Constants.POST_REQUEST, __name__))
        thread = Thread(target=perform_collection, args=(collector,))
        thread.start()
        return Constants.RECEIVED_SUCCESS_CODE, Constants.COLLECTION_RECEIVED_MESSAGE

    @staticmethod
    def collect_get(request, collector, logger):
        logger.info(get_log_string(request, Constants.GET_REQUEST, __name__))
        result = collector.manager.get_collection_status(collector.name)
        if not result:
            return Constants.SUCCESS_RESPONSE_CODE, Constants.NO_COLLECTION_FOUND_MESSAGE
        return Constants.SUCCESS_RESPONSE_CODE, json.dumps(result, default=str)

    @staticmethod
    def collect_delete(request, collector, logger):
        logger.info(get_log_string(request, Constants.DELETE_REQUEST, __name__))
        collector.manager.purge_prior_collections()
        return Constants.SUCCESS_RESPONSE_CODE, Constants.PURGE_REQUEST_MESSAGE

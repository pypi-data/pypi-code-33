import json
from nameko.web.handlers import HttpRequestHandler
from reliabilly.components.authorization import Authorization
from reliabilly.components.controllers.data_handler import DataHandler
from reliabilly.components.data.mongo_client import MongoDataClient
from reliabilly.components.health import HealthCheckProvider
from reliabilly.components.logger import LoggingProvider
from reliabilly.components.models.base import BaseModel
from reliabilly.components.monitoring import MonitoringProvider
from reliabilly.settings import Constants, Settings
from reliabilly.components.tools.version import version


class ExtendedHttpRequestHandler(HttpRequestHandler):
    def __init__(self, *args, **kwargs):
        self.original_request = None
        super().__init__(*args, **kwargs)

    def handle_request(self, request):
        self.original_request = request
        return super().handle_request(request)

    # pylint: disable=arguments-differ
    def response_from_result(self, *args, **kwargs):
        response = super(ExtendedHttpRequestHandler, self).response_from_result(*args, **kwargs)
        original_request = self.original_request
        if not Authorization.is_permitted(original_request):
            unauthorized_result = Authorization.get_unauthorized_response()
            response.set_data(unauthorized_result[2])
            response.status_code = unauthorized_result[0]
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Methods', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With, '
                             'Content-Type, Accept, Authorization')
        response.headers['Content-Type'] = 'application/json'
        return response


# pylint: disable=invalid-name
http = ExtendedHttpRequestHandler.decorator


def get_route(item=''):
    return f'/{Settings.SERVICE_NAME}/{item}'


def get_specific_item_route(sub_route):
    return get_route(f'{sub_route}<string:item_id>')


def get_item_route():
    return get_route('<string:item_id>')


# noinspection PyMethodParameters
class Meta(type):
    def __new__(cls, name, bases, dct):
        var = super().__new__(cls, name, bases, dct)
        var.name = Settings.SERVICE_NAME
        return var


def get_request_ip(request):
    return request.environ.get('HTTP_X_REAL_IP', request.remote_addr)


def get_log_string(request, method, name, item=Constants.EMPTY):
    return f'{name} {method} {item} {request.base_url} ' \
           f'{request.query_string} from {get_request_ip(request)} ' \
           f'auth {Authorization.get_auth_token_log(request)} ' \
           f'route {Constants.COMMA.join(request.access_route)} called...'


class DataController(metaclass=Meta):
    name = Settings.SERVICE_NAME
    model = BaseModel()
    monitor = MonitoringProvider()
    logger = LoggingProvider(name)

    def __init__(self, **kwargs):
        self.client = kwargs.get(Constants.CLIENT, MongoDataClient(table=self.name))
        self.model = kwargs.get(Constants.MODEL, BaseModel())
        self.data_handler = DataHandler(self.client)
        self.healthcheck = HealthCheckProvider(mongo=self.client)

    # pylint: disable=no-self-use
    @http(Constants.OPTIONS_REQUEST, get_route())
    def options(self, _):
        return Constants.SUCCESS_RESPONSE_CODE, version()

    # pylint: disable=no-self-use
    @http(Constants.OPTIONS_REQUEST, get_item_route())
    def options_item(self, _, item_id):
        return Constants.SUCCESS_RESPONSE_CODE, item_id

    @http(Constants.GET_REQUEST, get_route())
    def get(self, request):
        self.logger.info(get_log_string(request, Constants.GET_REQUEST, self.name))
        result = self.data_handler.handle_get_request(request)
        return result

    @http(Constants.GET_REQUEST, get_item_route())
    def get_one(self, request, item_id):
        self.logger.info(get_log_string(request, Constants.GET_REQUEST, self.name))
        return self.data_handler.handle_get_request_single(item_id)

    # pylint: disable=no-self-use
    @http(Constants.GET_REQUEST, get_route(Constants.PING_ROUTE))
    def ping(self, _):
        return Constants.SUCCESS_RESPONSE_CODE, Constants.PING_RESPONSE

    @http(Constants.GET_REQUEST, get_route(Constants.COUNT_ROUTE))
    def count(self, request):
        self.logger.info(get_log_string(request, Constants.GET_REQUEST, self.name))
        return self.data_handler.handle_count_request()

    @http(Constants.GET_REQUEST, get_route(Constants.HEALTH_ROUTE))
    def health(self, request):
        self.logger.info(get_log_string(request, Constants.GET_REQUEST, self.name, Constants.HEALTH))
        return Constants.SUCCESS_RESPONSE_CODE, self.healthcheck.check_health()

    @http(Constants.GET_REQUEST, get_route(Constants.VERSION_ROUTE))
    def version(self, request):
        self.logger.info(get_log_string(request, Constants.GET_REQUEST, self.name))
        return Constants.SUCCESS_RESPONSE_CODE, version()

    @http(Constants.POST_REQUEST, get_route())
    def post(self, request):
        self.logger.info(get_log_string(request, Constants.POST_REQUEST, self.name))
        payload = json.loads(request.get_data(as_text=True))
        if self.model.validate(payload):
            return self.data_handler.handle_post_request(payload)
        return Constants.UNPROCESSABLE_ENTITY_CODE, Constants.UNPROCESSABLE_ENTITY_MESSAGE

    @http(Constants.PUT_REQUEST, get_item_route())
    def put(self, request, item_id):
        self.logger.info(get_log_string(request, Constants.PUT_REQUEST, self.name))
        payload = json.loads(request.get_data(as_text=True))
        return self.data_handler.handle_update_request(item_id, payload)

    @http(Constants.POST_REQUEST, get_route(Constants.RESTORE_ROUTE))
    def restore(self, request):
        self.logger.info(get_log_string(request, Constants.POST_REQUEST, self.name))
        payload = json.loads(request.get_data(as_text=True))
        return self.data_handler.handle_restore_request(payload)

    @http(Constants.PUT_REQUEST, get_route())
    @http(Constants.DELETE_REQUEST, get_route())
    def bad_verbs(self, request):
        self.logger.info(get_log_string(request, Constants.PUT_REQUEST, self.name))
        return Constants.BAD_REQUEST_CODE, Constants.BAD_REQUEST_MESSAGE

    @http(Constants.DELETE_REQUEST, get_item_route())
    @http(Constants.DELETE_REQUEST, get_route())
    def delete(self, request, item_id):
        self.logger.info(get_log_string(request, Constants.DELETE_REQUEST, self.name, item_id))
        self.logger.info(f'{self.name} DELETE {item_id} called...')
        return self.data_handler.handle_delete_request(item_id)

    @http(Constants.POST_REQUEST, get_route(Constants.PURGE_ROUTE))
    def purge(self, request):
        self.logger.info(get_log_string(request, Constants.POST_REQUEST, self.name))
        return self.data_handler.handle_purge_request()

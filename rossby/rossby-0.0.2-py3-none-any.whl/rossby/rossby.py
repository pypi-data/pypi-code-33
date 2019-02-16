import requests
from collections import namedtuple
from string import Formatter
from urllib.parse import urljoin
from rossby.api_config import api_endpoints
from rossby.default_response import RossbyResponse


class RossbyAPIMeta(type):

    def __new__(mcs, name, bases, attrs):

        if 'base_url' not in attrs:
            attrs['base_url'] = 'https://api.weather.gov/'

        attrs['__init__'] = RossbyAPIMeta.get_init_method()
        attrs['session'] = requests.session()
        attrs['formatter'] = Formatter()

        for attr, method in RossbyAPIMeta.get_request_methods():
            setattr(mcs, attr, method)

        return super(RossbyAPIMeta, mcs).__new__(mcs, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        super(RossbyAPIMeta, cls).__init__(name, bases, attrs)

        RossbyAPIMeta.generate_api_methods(cls, attrs)

    @classmethod
    def get_init_method(mcs):
        def __init__(self, response_type='*/*'):
            # TODO: Need to investigate the behavior of this param...
            self.session.headers['Accept'] = response_type

        return __init__

    @classmethod
    def get_request_methods(mcs):
        def request(self, endpoint, **kwargs):

            formatters = (formatter for _, formatter, _, _ in self.formatter.parse(endpoint.endpoint) if formatter)

            url_params = {key: kwargs.pop(key) for key in formatters}
            url = urljoin(self.base_url, endpoint.endpoint.format(**url_params))

            query_params = {key: None for key in endpoint.param_keys}

            for key, value in kwargs.items():
                if type(value) in (list, tuple):
                    kwargs[key] = ','.join(str(v) for v in value)

            if endpoint.paginated and not kwargs.get('limit'):
                kwargs['limit'] = 10

            params = {'params' if endpoint.method == 'get' else 'data': {**query_params, **kwargs}}

            return self.request_response(url, endpoint, **params)

        def request_response(self, url, endpoint, **kwargs):
            response = self.session.request(endpoint.method, url, **kwargs)
            response.raise_for_status()

            if endpoint.response_type == RossbyResponse:
                return RossbyResponse(response.json(), api=self, endpoint=endpoint, response=response, source_url=url)
            else:
                return response

        yield 'request', request
        yield 'request_response', request_response

    @classmethod
    def generate_api_methods(mcs, api, attrs):
        make_request = lambda endpoint: lambda **kwargs: api.request(endpoint, **kwargs)

        for obj_name, endpoints in api_endpoints.items():
            methods = {endpoint_name: make_request(endpoint) for endpoint_name, endpoint in endpoints.items()}
            APIMethod = namedtuple('APIMethod_{}'.format(obj_name), methods.keys())

            setattr(api, obj_name, APIMethod(**methods))


class Rossby(object, metaclass=RossbyAPIMeta):
    pass

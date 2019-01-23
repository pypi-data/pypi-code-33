import json
import pickle
import requests
from requests.auth import HTTPBasicAuth
from reliabilly.settings import Settings, Constants, get_service_url, get_raw_service_url


def save_items(items, json_file, pickle_file):  # pragma: no cover
    with open(pickle_file, 'wb') as handle:
        pickle.dump(items, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(json_file, 'w') as file:
        json.dump(items, file)


class HttpRequestor:
    """ Generic web http(s) request client. """
    def __init__(self, **kwargs):
        self.client = kwargs.get(Constants.CLIENT, requests)
        self.save_fn = kwargs.get('save_fn', save_items)
        self.circuit_breaker = kwargs.get(Constants.CIRCUIT_BREAKER, None)

    def perform_web_request(self, verb, endpoint_url, **kwargs):
        if self.circuit_breaker is not None:
            return self.circuit_breaker.breaker.call(self._perform_web_request, verb, endpoint_url, **kwargs)
        return self._perform_web_request(verb, endpoint_url, **kwargs)

    def _perform_web_request(self, verb, endpoint_url, **kwargs):
        return self.client.request(verb, endpoint_url, **kwargs)

    def get(self, endpoint_url, **kwargs):
        return self._perform_web_request(Constants.GET_REQUEST, endpoint_url, **kwargs)

    def post(self, endpoint_url, **kwargs):
        return self._perform_web_request(Constants.POST_REQUEST, endpoint_url, **kwargs)

    def put(self, endpoint_url, **kwargs):
        return self._perform_web_request(Constants.PUT_REQUEST, endpoint_url, **kwargs)

    def delete(self, endpoint_url, **kwargs):
        return self._perform_web_request(Constants.DELETE_REQUEST, endpoint_url, **kwargs)

    def save_data_items(self, service_name, endpoint=Constants.EMPTY, paged=True):
        items = self.get_items(endpoint, paged, service_name)
        endpoint_name = endpoint.strip(Constants.FORWARD_SLASH)
        pickle_file = f'{service_name}{endpoint_name}.pickle'
        json_file = f'backup/{service_name}{endpoint_name}.json'
        self.save_fn(items, json_file, pickle_file)
        return True

    def get_items(self, endpoint, paged, service_name):
        if paged:
            return self.get_all_items(service_name)
        headers = self.get_request_headers()
        url = get_raw_service_url(service_name) + f'{endpoint}'
        return self.get(url, headers=headers).json()

    @staticmethod
    def get_request_headers():
        return {Constants.AUTHORIZATION_HEADER: Settings.AUTH_TOKEN, Constants.SERVICE_NAME_ENV: Settings.SERVICE_NAME}

    def get_all_items(self, service_name):
        url = get_service_url(service_name)
        results = list()
        current_offset = 0
        headers = self.get_request_headers()
        result = self._call_endpoint(url, current_offset, headers=headers)
        results.extend(result[service_name])
        while len(results) < result['total']:
            current_offset += result['limit']
            result = self._call_endpoint(url, current_offset, headers=headers)
            results.extend(result[service_name])
        return results

    def _call_endpoint(self, url, offset, headers=None):
        return self.get(url.format(offset=offset), headers=headers).json()

    @staticmethod
    def get_auth_value(user, password):
        return HTTPBasicAuth(user, password)

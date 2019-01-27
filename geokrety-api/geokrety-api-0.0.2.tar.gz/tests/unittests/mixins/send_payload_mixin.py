# -*- coding: utf-8 -*-

import importlib
import json
import pprint
import urllib

from app import current_app


class SendPayloadMixin(object):
    def __init__(self, *args, **kwargs):
        super(SendPayloadMixin, self).__init__(*args, **kwargs)
        self.app = current_app.test_client()
        self._check_urls()

    def _check_urls(self):
        assert hasattr(self, '_url'), \
            "{} class is missing '_url' attribute" \
            .format(self.__class__.__name__)
        assert hasattr(self, '_url_collection'), \
            "{} class is missing '_url_collection' attribute" \
            .format(self.__class__.__name__)

    def _send(self,
              method,
              endpoint,
              code=200,
              payload=None,
              user=None,
              content_type='application/vnd.api+json',
              args=None):
        """
        Send a POST request to the api, and check expected response code.
        """
        if not payload:
            payload = {}

        headers = {}
        if user:
            headers['Authorization'] = \
                'JWT %s' % self._login(user.name, user.password)

        args_ = '' if args is None else urllib.urlencode(args)
        endpoint = "{}?{}".format(endpoint, args_)

        with current_app.test_request_context():
            print("URL: {}".format(endpoint))
            print("METHOD: {}".format(method))
            print("PAYLOAD: {}".format(pprint.pformat(payload)))
            response = getattr(self.app, method)(endpoint,
                                                 json=payload,
                                                 headers=headers,
                                                 content_type=content_type)

            data = response.get_data(as_text=False)
            if response.content_type in ['application/vnd.api+json', 'application/json'] and data:
                data = json.loads(data)

            print("RESPONSE: {}".format(pprint.pformat(data)))

            assert response.status_code == code, \
                "Expect response code {} but was {}"\
                .format(code, response.status_code)
            return self._get_response_class(response.get_json())

    def _login(self, username="kumy", password="password"):
        """
        Obtain a JWT token to authenticate next requests
        """
        response = self.app.post('/auth/session',
                                 headers={
                                     'content-type': 'application/json'
                                 },
                                 data=json.dumps({
                                     "username": username,
                                     "password": password
                                 }), follow_redirects=True)

        assert response.status_code == 200
        assert 'Content-Type' in response.headers
        assert response.headers['Content-Type'] == 'application/json'
        raised = False
        try:
            data = json.loads(response.data)
        except Exception:  # pragma: no cover
            raised = True
        assert raised != 'Failed to decode json'
        assert 'access_token' in data
        return data['access_token']

    def _get_response_class(self, json_data):
        assert hasattr(self, 'type'), \
            "{} class is missing 'type' attribute" \
            .format(self.__class__.__name__)
        module = "tests.unittests.utils.responses.{}"\
            .format(self.type)\
            .replace('-', '_')
        try:
            responseClass = getattr(importlib.import_module(module),
                                    self._response_type)
        except AttributeError:  # pragma: no cover
            assert False, "Module '{}' has no class '{}'".format(
                module, self._response_type
            )
        return responseClass(json_data)

    def _set_response_class(self, name):
        self._response_type = name

    def get(self, obj_id, *arg, **kwargs):
        self._set_response_class(self._response_type)
        return self._send('get', self._url.format(obj_id), *arg, **kwargs)

    def get_collection(self, *arg, **kwargs):
        self._set_response_class(self._response_type_collection)
        return self._send('get', self._url_collection, *arg, **kwargs)

    def post(self, *arg, **kwargs):
        self._set_response_class(self._response_type)
        if 'payload' not in kwargs:
            kwargs['payload'] = self
        if 'code' not in kwargs:
            kwargs['code'] = 201
        return self._send('post', self._url_collection, *arg, **kwargs)

    def patch(self, obj_id, *arg, **kwargs):
        self._set_response_class(self._response_type)
        self.set_id(obj_id)
        if 'payload' not in kwargs:
            kwargs['payload'] = self
        return self._send('patch', self._url.format(obj_id), *arg, **kwargs)

    def delete(self, obj_id, *arg, **kwargs):
        self._set_response_class(self._response_type)
        return self._send('delete', self._url.format(obj_id), *arg, **kwargs)

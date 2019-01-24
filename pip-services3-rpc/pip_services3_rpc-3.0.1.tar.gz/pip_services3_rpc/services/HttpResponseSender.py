# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.HttpResponseSender
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    HttpResponseSender implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json

import bottle
from pip_services3_commons.errors import ErrorDescriptionFactory


class HttpResponseSender():
    """
    Helper class that handles HTTP-based responses.
    """
    @staticmethod
    def send_result(result, to_json):
        bottle.response.headers['Content-Type'] = 'application/json'
        if result == None:
            bottle.response.status = 404
            return
        else:
            bottle.response.status = 200
            return json.dumps(result, default=to_json)

    @staticmethod
    def send_created_result(result, to_json):
        bottle.response.headers['Content-Type'] = 'application/json'
        if result == None:
            bottle.response.status = 404
            return
        else:
            bottle.response.status = 201
            return json.dumps(result, default=to_json)

    @staticmethod
    def send_deleted_result():
        bottle.response.headers['Content-Type'] = 'application/json'
        bottle.response.status = 204
        return

    @staticmethod
    def send_error(error):
        """
        Sends error serialized as ErrorDescription object and appropriate HTTP status code. If status code is not defined, it uses 500 status code.

        :param error: an error object to be sent.

        :return: HTTP response status
        """
        bottle.response.headers['Content-Type'] = 'application/json'
        error = ErrorDescriptionFactory.create(error)
        bottle.response.status = error.status
        return json.dumps(error.to_json())

    def get_correlation_id(self):
        return bottle.request.query.get('correlation_id')
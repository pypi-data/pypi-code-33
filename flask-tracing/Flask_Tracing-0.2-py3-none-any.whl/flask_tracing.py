# -*- coding: utf-8 -*-
import uuid
import logging

from flask import request, g, has_request_context


def generate_request_id(original_id=''):
    """Generate request id."""
    new_id = uuid.uuid4()

    if original_id:
        new_id = '{}, {}'.format(original_id, new_id)

    return new_id


def get_request_id(self):
    """Get current request id in session."""
    if 'request_id' not in g:
        original_id = request.headers.get('x-request-id')
        g.request_id = generate_request_id(original_id)
    return g.request_id


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id() if has_request_context() else ''
        return True


class Tracing(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.after_request(self.hook)
        pass

    def hook(self, response):
        response.headers['X-Request-ID'] = get_request_id()

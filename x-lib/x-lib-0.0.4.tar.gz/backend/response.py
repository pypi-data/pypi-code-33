from flask import Response, jsonify
from .logger import logging

log = logging.getLogger(__name__)


class JsonResponse(Response):
    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, dict):
            data = {}
            if 'status' not in rv:
                data.update({'status': True})
            else:
                data.update({'status': rv['status']})
                rv.pop('status')
            if 'message' in rv:
                data.update({'message': rv['message']})
                rv.pop('message')
            if 'key' in rv:
                data.update({'key': rv['key']})
                rv.pop('key')
            if 'total' in rv:
                data.update({'total': rv['total']})
                rv.pop('total')
            if 'total_pages' in rv:
                data.update({'total_pages': rv['total_pages']})
                rv.pop('total_pages')
            data.update({'data': rv})

            return super(JsonResponse, cls).force_type(jsonify(data), environ)
        return super(JsonResponse, cls).force_type(rv, environ)

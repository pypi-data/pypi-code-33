from typing import Callable

from http_server_base.tools import JsonSerializable
from tornado.web import RequestHandler
import json

def error_decorator(func:Callable) -> Callable:
    def resp_error(handler:RequestHandler, code=500, reason=None, message=None, *args, **kwargs):
        handler.clear()
        handler.logger.info('{0}' if reason else '{0}: {1}', code, reason, prefix='resp')
        handler.set_status(code, reason=reason)
        if not (message is None):
            handler.logger.warning('{}', message, prefix='resp')
        func(handler, code=handler._status_code, reason=handler._reason, message=message, *args, **kwargs)
        handler.finish()
    return resp_error

def success_decorator(func):
    def resp_success(handler:RequestHandler, code=200, reason=None, message=None, result=None, *args, **kwargs):
        handler.logger.info('{0}' if reason else '{0}: {1}', code, reason, prefix='resp')
        handler.set_status(code, reason=reason)
        if not (message is None):
            handler.logger.debug('{}', message, prefix='resp')
        if not (result is None):
            handler.logger.debug('{}', result, prefix='resp')
        func(handler, code=handler._status_code, reason=handler._reason, message=message, result=result, *args, **kwargs)
    return resp_success

class BasicResponder:
    """
    Works ONLY for the Logged_RequestHandler's
    """
    @staticmethod
    @error_decorator
    def resp_error(handler:RequestHandler, code, reason, message):
        pass
    @staticmethod
    @success_decorator
    def resp_success(handler:RequestHandler, code, reason, message, result):
        pass

class TextBasicResponder(BasicResponder):
    @staticmethod
    @error_decorator
    def resp_error(handler:RequestHandler, code=500, reason=None, message=None):
        pass

    @staticmethod
    @success_decorator
    def resp_success(handler:RequestHandler, code=200, reason=None, message=None, result=None):
        if (result):
            handler.set_header('Content-Type', 'text/plain')
            handler.write(bytes(str(result), 'utf8'))

class HtmlBasicResponder(BasicResponder):
    @staticmethod
    @error_decorator
    def resp_error(handler: RequestHandler, code=500, reason=None, message=None):
        _html = f'<html><title>{code}: {reason}</title><body>{message}</body></html>'
        handler.write(bytes(_html, 'utf8'))
    
    @staticmethod
    @success_decorator
    def resp_success(handler: RequestHandler, code=200, reason=None, message=None, result=None):
        if (not result is None):
            handler.set_header('Content-Type', 'text/html')
            _html = f'<html><title>{code}: {reason}</title><body>{message}:<br/>{str(result)}</body></html>'
            handler.write(bytes(_html, 'utf8'))

class JsonCustomResponder(BasicResponder):
    def _make_response(handler:RequestHandler, *args, response: JsonSerializable=None, **kwargs):
        _resp_str = json.dumps(response, sort_keys=True)
        handler.logger.debug(_resp_str, prefix='resp')
        handler.set_header('Content-Type', 'application/json')
        handler.write(bytes(_resp_str, 'utf8'))
    
    resp_error = error_decorator(_make_response)
    resp_success = success_decorator(_make_response)

class JsonBasicResponder(BasicResponder):
    @staticmethod
    @error_decorator
    def resp_error(handler:RequestHandler, reason=None, message=None, **kwargs):
        handler.set_header('Content-Type', 'application/json')
        _json = dict(success=False, **kwargs)
        if (reason is not None):
            _json['reason'] = reason
        if (message is not None):
            _json['message'] = message
        handler.write(bytes(json.dumps(_json), 'utf8'))

    @staticmethod
    @success_decorator
    def resp_success(handler:RequestHandler, reason=None, message=None, result=None, **kwargs):
        handler.set_header('Content-Type', 'application/json')
        _json = dict(success=True, **kwargs)
        if (reason is not None):
            _json['reason'] = reason
        if (message is not None):
            _json['message'] = message
        if (result is not None):
            _json['result'] = result
        handler.write(bytes(json.dumps(_json), 'utf8'))

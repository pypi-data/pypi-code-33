import re
import logging
import traceback
from collections import Iterable
import grpc
import sys
from google.protobuf.json_format import MessageToDict, ParseDict

from grpc_help.exceptions import RpcException, NotAuthenticatedError
from grpc_help.utils import json_encode, async_to_sync

logger = logging.getLogger(__name__)
SENSITIVE_CREDENTIALS = re.compile('api|token|key|secret|password|signature|pwd', re.I)
CLEANSED_SUBSTITUTE = "********************"


class GenericRpcView:
    auth_user_meta_key = "auth_user"
    proto_response_class = None
    requires_authentication = False

    def __init__(self, request, content):
        assert self.proto_response_class, "Missing proto_response_class declaration"
        self.request = request
        self._data = None
        self.content = content

    @property
    def data(self):
        if self._data is not None:
            return self._data

        if isinstance(self.request, Iterable):
            self._data = tuple(MessageToDict(r, preserving_proto_field_name=True)
                               for r in self.request)
        else:
            self._data = MessageToDict(self.request, preserving_proto_field_name=True)

        return self._data

    def perform_authentication(self):
        if not self.requires_authentication:
            return

        user_data = dict(self.content.invocation_metadata()).get(self.auth_user_meta_key, None)
        if not user_data:
            raise NotAuthenticatedError

    def view_handle(self, *args, **kwargs):
        raise NotImplementedError

    def finalize_response(self, response):
        proto_response_instance = self.proto_response_class()
        return ParseDict(response, proto_response_instance, ignore_unknown_fields=True)

    def __call__(self, *args, **kwargs):
        try:
            self.perform_authentication()
            result = self.view_handle(*args, **kwargs)
            return self.finalize_response(result)
        except Exception as e:
            self.exception_handle(e)
            return self.proto_response_class()

    @staticmethod
    def clean_credentials(credentials):
        if isinstance(credentials, (type(None), list, tuple, set)):
            return credentials

        result = {}
        for key, value in credentials.items():
            key = key.decode() if isinstance(key, bytes) else str(key)
            if SENSITIVE_CREDENTIALS.search(key):
                result[key] = CLEANSED_SUBSTITUTE
            else:
                result[key] = value

        return result

    def record_log(self, status_code, exc_info, **kwargs):
        params = self.clean_credentials(self.data)
        exc = exc_info[1]
        if hasattr(exc, "message"):
            error_info = exc.message
        elif hasattr(exc, "messages"):
            error_info = exc.messages
        elif hasattr(exc, "detail"):
            error_info = exc.detail
        else:
            error_info = ""

        log_context = {
            "request_protocol": "grpc",
            "invocation_metadata": dict(self.content.invocation_metadata()),
            "request_data": params,
            "status_code": str(status_code),
            "reason": error_info,
        }
        if kwargs:
            log_context.update(**kwargs)

        log_context = json_encode(log_context)
        logger.error(log_context, exc_info=True)

    def exception_handle(self, exc):
        if issubclass(exc.__class__, RpcException):
            status_code, message = exc.status_code, str(exc)
        else:
            status_code = grpc.StatusCode.UNKNOWN
            exc_info = sys.exc_info()
            try:
                self.record_log(status_code, exc_info)
            except Exception:
                logger.error("Exception in exception handler", exc_info=True)

            status_code = grpc.StatusCode.UNKNOWN
            message = f"{exc}; reason: {traceback.format_exc()}"

        self.content.set_code(status_code)
        self.content.set_details(message)


class StreamRpcView(GenericRpcView):
    def __call__(self, *args, **kwargs):
        try:
            self.perform_authentication()
            results = self.view_handle(*args, **kwargs)
            for result in results:
                yield self.finalize_response(result)
        except Exception as e:
            self.exception_handle(e)
            yield self.proto_response_class()


class AsyncGenericRpcView(GenericRpcView):
    async def view_handle(self, *args, **kwargs):
        raise NotImplementedError

    @async_to_sync
    async def __call__(self, *args, **kwargs):
        try:
            self.perform_authentication()
            result = await self.view_handle(*args, **kwargs)
            return self.finalize_response(result)
        except Exception as e:
            self.exception_handle(e)
            return self.proto_response_class()


class AsyncStreamRpcView(AsyncGenericRpcView):
    @async_to_sync
    async def __call__(self, *args, **kwargs):
        try:
            self.perform_authentication()
            results = self.view_handle(*args, **kwargs)
            if hasattr(results, "__aiter__"):
                async for result in results:
                    yield self.finalize_response(result)
            else:
                yield self.finalize_response(await results)

        except Exception as e:
            self.exception_handle(e)
            yield self.proto_response_class()


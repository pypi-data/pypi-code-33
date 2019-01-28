import json

from dobby.responses.base.builder.base_response_builder import BaseResponseBuilder
from dobby.responses.http.response.http_response import HttpResponse


class HTTPResponseBuilder(BaseResponseBuilder):

    def __init__(self):
        super().__init__()

    def create_response(self, result):

        status_code = result.status_code
        print(status_code)
        response_body = self._prepare_jsonified_response_body(result)
        return HttpResponse(status_code, response_body).format()

    def _prepare_jsonified_response_body(self, result):
        response_body = self._prepare_response_body(result)
        return json.dumps(response_body, default=lambda x: x.__dict__)

    def _prepare_response_body(self, result):
        failed = result.failed
        message = result.message
        data = result.data

        response_body = dict()
        response_body.update({"__failed": failed})
        if data:
            response_body.update({"data": data})
        if message:
            response_body.update({"message": message})

        print(response_body)
        return response_body

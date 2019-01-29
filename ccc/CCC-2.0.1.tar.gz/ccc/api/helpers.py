import json

from django.http import HttpResponse


class ApiResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = json.dumps(data)
        kwargs['content_type'] = 'application/json'
        super(ApiResponse, self).__init__(content, **kwargs)

# Helper for parse json data from request


def request_parse(request):
    return json.loads(request.body.decode(encoding='UTF-8'))

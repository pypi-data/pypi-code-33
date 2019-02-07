import json

from serenytics import settings
from serenytics.helpers import make_request, HTTP_201_CREATED
from serenytics.webapp import WebApp


def create_webapp(client, name, json_content=None):
    json_content = json_content or {}
    response = make_request('post', settings.SERENYTICS_API_DOMAIN + '/api/web_app',
                            data=json.dumps({'name': name, 'jsonContent': json_content}),
                            headers=client._headers,
                            expected_status_code=HTTP_201_CREATED)
    return WebApp(config=response.json(), client=client)

import datetime
import hashlib
import hmac
import base64
import json
import asyncio
import pprint
from uuid import UUID
from aiohttp import ClientSession
from .utils import find_request

PP = pprint.PrettyPrinter(indent=4)

class OMSLoggingClient:
    def __init__(self, settings={}, version='2016-04-01', *args, **kwargs):
        self.workspace_id = settings.get('workspace_id')
        self.workspace_secret = settings.get('workspace_secret')
        self.version = version
        self._url = "https://{}.ods.opinsights.azure.com/api/logs?api-version={}".format(
            self.workspace_id, self.version)
        self._session = ClientSession(loop=kwargs.get('loop', asyncio.get_event_loop()))
        self.print_events = settings.get("print_events")
        self.request_headers = settings.get("request_headers", {})
        self.source = settings.get("source")

    def _signature(self, date, content_length):
        sigs= "POST\n{}\napplication/json\nx-ms-date:{}\n/api/logs".format(
            str(content_length), date)
        utf8_sigs = sigs.encode('utf-8')
        decoded_shared_key = base64.b64decode(self.workspace_secret)
        hmac_sha256_sigs = hmac.new(
            decoded_shared_key, msg=utf8_sigs, digestmod=hashlib.sha256).digest()
        encoded_hash = base64.b64encode(hmac_sha256_sigs)
        encoded_hash = str(encoded_hash).strip('b').strip("'")
        authorization = "SharedKey {}:{}".format(self.workspace_id, encoded_hash)
        return authorization

    async def format_request(self, request):
        if request == None:
            return {}
        else:
            request_data = {
                'path': request.path,
                'host': request.host,
                'method': request.method,
                'content_type': request.content_type,
                'client_ip': request.remote,
                'scheme': request.scheme,
            }
            if request.match_info.route.resource:
                resource_info = request.match_info.route.resource.get_info()
                request_data['route'] = resource_info.get('formatter', request.path)
            else:
                request_data['route'] = request.path
            if self.request_headers:
                for log_key, header_key in self.request_headers.items():
                    request_data[log_key] = request.headers.get(header_key, 'NA')
            params = {}
            if request.method != "GET":
                try:
                    post_data = await request.json()
                    params.update(post_data)
                except:
                    pass
            if request.match_info:
                params.update(request.match_info)
            if request.query:
                params.update(dict(request.query))
            if params:
                request_data['params'] = json.dumps(params)
            return request_data

    async def format_event_data(self, obj):
        if obj is None:
            return {}
        cleaned_object_data = {}
        if 'to_json' in dir(obj):
            for k, v in obj.to_json().items():
                cleaned_object_data[k] = v

        elif isinstance(obj, dict):
            for key, value in obj.items():
                if type(value) is datetime.datetime:
                    cleaned_object_data[key] = value.strftime('%m/%d/%Y %H:%M:%S')
                elif type(value) is UUID:
                    cleaned_object_data[key] = str(value)
                elif type(value) is dict:
                    cleaned_object_data[key] = json.dumps(value)
                else:
                    cleaned_object_data[key] = value
        else:
            for oa in [x for x in obj.__dict__ if not x.startswith('_')]:
                if type(getattr(obj, oa)) is datetime.datetime:
                    cleaned_object_data[oa] = getattr(obj, oa).strftime('%m/%d/%Y %H:%M:%S')
                elif type(getattr(obj, oa)) is UUID:
                    cleaned_object_data[oa] = str(getattr(obj, oa))
                else:
                    cleaned_object_data[oa] = getattr(obj, oa)
        return cleaned_object_data


    async def create_event(self, *args, **kwargs):
        event_time = kwargs.get('event_time', datetime.datetime.utcnow()).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        signature_time = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

        event_data = await self.format_event_data(kwargs.get('event_data'))
        if kwargs.get('name'):
            event_data['name'] = kwargs.get('name')
        request_data = await self.format_request(kwargs.get('request', find_request()))
        body = json.dumps({
            **request_data,
            **event_data,
            "TimeCollected": event_time
        })
        if self.print_events:
            PP.pprint((f"--{event_data.get('name')}--",
                       event_time,
                       request_data,
                       event_data,))
            print('\n')
        content_length = len(body)
        signature = self._signature(signature_time, content_length)

        headers = {
            'content-type': 'application/json',
            'Authorization': signature,
            'Log-Type': kwargs.get('log_type', 'serverLog'),
            'x-ms-date': signature_time,
            'time-generated-field': "TimeCollected"
        }
        await self.send_to_oms(body, headers)

    async def send_to_oms(self, body, headers):
        async with self._session.post(self._url,\
                      headers=headers,\
                      data=body) as response:
            if response.status > 299:
                print('oms_logger_error: {0} - {1}'.format(
                    response.status, response.text))

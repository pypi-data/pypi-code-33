
import aiohttp
import asyncio
import json
import jsonschema

from colibris import schemas
from colibris import settings

from testmyesp import attributes
from testmyesp import schemafields
from testmyesp import utils
from testmyesp.instructions import BaseInstruction, register_instruction, InstructionException


class HTTPClientException(InstructionException):
    pass


class ResponseTimeout(HTTPClientException):
    def __init__(self, timeout):
        self.timeout = timeout
        super().__init__('no response received within {} seconds'.format(timeout))


class UnexpectedStatus(InstructionException):
    def __init__(self, expected_status, received_status, received_body):
        self.expected_status = expected_status
        self.received_status = received_status
        self.received_body = received_body

    def __str__(self):
        try:
            received_body = self.received_body.decode().replace('\n', '\\n')

        except UnicodeDecodeError:
            received_body = None

        if received_body is not None:
            return 'expected status {expected}, got {received}; body was "{body}"'.format(expected=self.expected_status,
                                                                                          received=self.received_status,
                                                                                          body=received_body)

        else:
            return 'expected status {expected}, got {received}'.format(expected=self.expected_status,
                                                                       received=self.received_status)


class UnexpectedHeader(InstructionException):
    def __init__(self, name, expected_header, received_header, received_body):
        self.name = name
        self.expected_header = expected_header
        self.received_header = received_header
        self.received_body = received_body

    def __str__(self):
        if self.received_header is None:
            msg = 'missing header {name} = "{expected}"'.format(name=self.name, expected=self.expected_header)

        else:
            msg = 'expected header {name} = "{expected}", got "{received}"'.format(name=self.name,
                                                                                   expected=self.expected_header,
                                                                                   received=self.received_header)

        try:
            received_body = self.received_body.decode().replace('\n', '\\n')
            msg += '; body was "{body}"'.format(body=received_body)

        except UnicodeDecodeError:
            pass

        return msg


class UnexpectedBody(InstructionException):
    def __init__(self, expected_body, received_body):
        self.expected_body = expected_body
        self.received_body = received_body

    def __str__(self):
        if not isinstance(self.expected_body, bytes) or not isinstance(self.received_body, bytes):
            return 'unexpected body'

        try:
            expected_body = self.expected_body.decode().replace('\n', '\\n')
            received_body = self.received_body.decode().replace('\n', '\\n')
            return 'expected body "{expected}", got "{received}"'.format(expected=expected_body, received=received_body)

        except UnicodeDecodeError:
            return 'unexpected body'


class UnexpectedJSONBody(UnexpectedBody):
    def __str__(self):
        expected_body = json.dumps(self.expected_body)
        received_body = json.dumps(self.received_body)

        return 'expected body {expected}, got {received}'.format(expected=expected_body, received=received_body)


class InvalidJSONBody(InstructionException):
    def __init__(self, body):
        self.body = body

    def __str__(self):
        try:
            body = self.body.decode().replace('\n', '\\n')
            return 'invalid JSON body "{body}"'.format(body=body)

        except UnicodeDecodeError:
            return 'invalid JSON body'


class JSONBodySchemaValidationError(InstructionException):
    def __init__(self, expected_body_schema, received_body, exception):
        self.expected_body_schema = expected_body_schema
        self.received_body = received_body
        self.exception = exception

    def __str__(self):
        received_body = json.dumps(self.received_body)

        return 'JSON body schema validation error: {}; body was {}'.format(self.exception.message, received_body)


@register_instruction
class HTTPClient(BaseInstruction):
    NAME = 'http-client'

    DEFAULT_TIMEOUT = 60

    def __init__(self, method, path, ip_address=None, schema=None, port=None,
                 headers=None, body=None, body_bytes=None,
                 expected_status=200, expected_headers=None, expected_body=None, expected_body_bytes=None,
                 timeout=None):

        self.method = method
        self.path = path
        self.ip_address = ip_address
        self.schema = schema or 'http'
        self.port = port if port is not None else (80 if self.schema == 'http' else 443)

        if not self.path.startswith('/'):
            self.path = '/' + self.path

        self.headers = headers or {}

        if body_bytes is not None:
            prepared_body = self.prepare_body(body_bytes)

        elif body is not None:
            prepared_body = self.prepare_body(body)

        else:
            prepared_body = None

        if isinstance(prepared_body, str):
            prepared_body = prepared_body.encode()

        self.body = prepared_body

        self.expected_status = expected_status
        self.expected_headers = expected_headers

        if expected_body is not None and isinstance(expected_body, str):
            self.expected_body = expected_body.encode()

        elif expected_body_bytes is not None:
            self.expected_body = expected_body_bytes

        else:
            self.expected_body = expected_body

        self.timeout = timeout or self.DEFAULT_TIMEOUT

        super().__init__()

    def execute(self):
        ip_address = self.ip_address or attributes.get(attributes.DEVICE_IP_ADDRESS)
        if not ip_address:
            raise HTTPClientException('cannot find device IP address')

        url = 'http://{ip_address}:{port}{path}'
        url = url.format(ip_address=ip_address, port=self.port, path=self.path)

        body_str = None
        if isinstance(self.body, bytes):
            try:
                body_str = self.body.decode()

            except UnicodeDecodeError:
                pass

        if body_str is not None:
            self.logger.debug('HTTP request %s %s:\n    %s', self.method, url, body_str)

        else:
            self.logger.debug('HTTP request %s %s', self.method, url)

        utils.run_sync(self.do_request(url))

    async def do_request(self, url):
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(self.method, url, headers=self.headers, data=self.body) as response:
                    received_body = await response.read()
                    self.logger.debug('received response')

                    if response.status != self.expected_status:
                        raise UnexpectedStatus(self.expected_status, response.status, received_body)

                    if self.expected_headers:
                        for name, value in self.expected_headers.items():
                            if response.headers.get(name) != value:
                                raise UnexpectedHeader(name, value, response.headers.get(name), received_body)

                    received_body = self.parse_received_body(received_body)
                    self.verify_received_body(received_body)

        except asyncio.TimeoutError:
            raise ResponseTimeout(self.timeout)

    def prepare_body(self, body):
        return body

    def parse_received_body(self, body):
        return body

    def verify_received_body(self, received_body):
        if (self.expected_body is not None) and (received_body != self.expected_body):
            raise UnexpectedBody(self.expected_body, received_body)

    class Schema(schemas.Schema):
        method = schemas.fields.String(required=True,
                                       validate=schemas.validate.OneOf(['GET', 'HEAD', 'OPTIONS', 'POST', 'PUT',
                                                                        'PATCH', 'DELETE', 'TRACE', 'CONNECT']))

        path = schemas.fields.String(required=True, validate=schemas.validate.Length(min=1, max=2048))
        ip_address = schemas.fields.String(validate=schemas.validate.Regexp(r'^[0-9.]{7,15}$'))
        schema = schemas.fields.String(validate=schemas.validate.OneOf(['http', 'https']))
        port = schemas.fields.Integer(validate=schemas.validate.Range(0, 65535))

        headers = schemas.fields.Dict(keys=schemas.fields.String(validate=[schemas.validate.Length(1, 256),
                                                                           schemas.validate.Regexp(r'^[\w-]+$')]),
                                      values=schemas.fields.String(validate=schemas.validate.Length(1, 256)))
        body = schemas.fields.String(validate=schemas.validate.Length(min=1, max=65536))
        body_bytes = schemafields.Base64Field()

        expected_status = schemas.fields.Integer(validate=schemas.validate.Range(100, 599))
        expected_headers = schemas.fields.Dict(keys=schemas.fields.String(validate=[schemas.validate.Length(1, 256),
                                                                                    schemas.validate.Regexp(r'^[\w-]+$')]),
                                               values=schemas.fields.String(validate=schemas.validate.Length(1, 256)))
        expected_body = schemas.fields.String(validate=schemas.validate.Length(min=1, max=65536), allow_none=True)
        expected_body_bytes = schemafields.Base64Field()

        timeout = schemas.fields.Integer(validate=schemas.validate.Range(1, settings.MAX_JOB_TIME))


@register_instruction
class JSONHTTPClient(HTTPClient):
    NAME = 'json-http-client'

    def __init__(self, method, path, ip_address=None, schema=None, port=None,
                 headers=None, body=None,
                 expected_status=200, expected_headers=None, expected_body=None, expected_body_schema=None,
                 timeout=None):

        self.expected_body_schema = expected_body_schema

        super().__init__(method=method, path=path, ip_address=ip_address, schema=schema, port=port,
                         headers=headers, body=body,
                         expected_status=expected_status, expected_headers=expected_headers,
                         expected_body=expected_body, timeout=timeout)

    def prepare_body(self, body):
        return json.dumps(body).encode()

    def parse_received_body(self, body):
        try:
            body_str = body.decode()

        except UnicodeDecodeError:
            raise InvalidJSONBody(body)

        if body_str.strip() == '':  # empty body treated as null
            return None

        try:
            return json.loads(body_str)

        except json.JSONDecodeError:
            raise InvalidJSONBody(body)

    def verify_received_body(self, received_body):
        if (self.expected_body is not None) and (received_body != self.expected_body):
            raise UnexpectedJSONBody(self.expected_body, received_body)

        if self.expected_body_schema is not None:
            try:
                jsonschema.validate(received_body, schema=self.expected_body_schema)

            except jsonschema.ValidationError as e:
                raise JSONBodySchemaValidationError(self.expected_body, received_body, e)

    class Schema(HTTPClient.Schema):
        expected_body_schema = schemas.fields.Raw()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields['body'] = schemas.fields.Raw()
            self.fields['expected_body'] = schemas.fields.Raw(allow_none=True)

            self.fields.pop('body_bytes')
            self.fields.pop('expected_body_bytes')

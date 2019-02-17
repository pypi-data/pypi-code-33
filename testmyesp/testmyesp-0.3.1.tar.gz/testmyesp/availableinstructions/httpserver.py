
import asyncio
import json
import jsonschema

from aiohttp import web

from colibris import schemas
from colibris import settings

from testmyesp import schemafields
from testmyesp import utils
from testmyesp.instructions import BaseInstruction, register_instruction, InstructionException


class HTTPServerException(InstructionException):
    pass


class RequestTimeout(HTTPServerException):
    def __init__(self, timeout):
        self.timeout = timeout
        super().__init__('no request received within {} seconds'.format(timeout))


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
class HTTPServer(BaseInstruction):
    NAME = 'http-server'

    DEFAULT_TIMEOUT = 60

    def __init__(self,
                 expected_method, expected_path, expected_headers=None, expected_body=None, expected_body_bytes=None,
                 status=200, headers=None, body=None, body_bytes=None,
                 port=None, timeout=None):

        self.expected_method = expected_method
        self.expected_path = expected_path
        self.expected_headers = expected_headers
        self.expected_body = expected_body
        self.expected_body_bytes = expected_body_bytes

        self.status = status
        self.headers = headers or {}
        self.body = body
        self.body_bytes = body_bytes

        self.port = port or 8080
        self.timeout = timeout or self.DEFAULT_TIMEOUT

        if not self.expected_path.startswith('/'):
            self.expected_path = '/' + self.expected_path

        if expected_body is not None and isinstance(expected_body, str):
            self.expected_body = expected_body.encode()

        elif expected_body_bytes is not None:
            self.expected_body = expected_body_bytes

        else:
            self.expected_body = expected_body

        if body_bytes is not None:
            prepared_body = self.prepare_body(body_bytes)

        elif body is not None:
            prepared_body = self.prepare_body(body)

        else:
            prepared_body = None

        if isinstance(prepared_body, str):
            prepared_body = prepared_body.encode()

        self.body = prepared_body

        self.server_task = None
        self.runner = None
        self.request_validation_error = None

        super().__init__()

    def execute(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.server_task = asyncio.ensure_future(self.run_server())

        try:
            asyncio.get_event_loop().run_until_complete(self.server_task)

        except asyncio.CancelledError:
            pass  # this is what we expect on a successful execution

        finally:
            utils.run_sync(self.runner.cleanup())

        if self.request_validation_error:
            raise self.request_validation_error

    async def run_server(self):
        self.logger.debug('waiting for %s %s request on port %d', self.expected_method, self.expected_path, self.port)

        app = web.Application()
        app.router.add_route(self.expected_method, self.expected_path, self.handle_request)

        self.runner = web.AppRunner(app)
        await self.runner.setup()

        site = web.TCPSite(self.runner, '0.0.0.0', self.port)
        await site.start()

        # normally, on a successful execution, this task is cancelled
        await asyncio.sleep(self.timeout)
        raise RequestTimeout(self.timeout)

    async def handle_request(self, request):
        received_body = await request.read()
        self.logger.debug('received request')

        try:
            self.verify_request(received_body, request.headers)

        except Exception as e:
            # pass exceptions to main instruction coroutine
            self.request_validation_error = e

        self.server_task.cancel()

        return self.prepare_response()

    def verify_request(self, body, headers):
        if self.expected_headers:
            for name, value in self.expected_headers.items():
                if headers.get(name) != value:
                    raise UnexpectedHeader(name, value, headers.get(name), body)

        body = self.parse_received_body(body)
        self.verify_received_body(body)

    def prepare_body(self, body):
        return body

    def parse_received_body(self, body):
        return body

    def verify_received_body(self, received_body):
        if (self.expected_body is not None) and (received_body != self.expected_body):
            raise UnexpectedBody(self.expected_body, received_body)

    def prepare_response(self):
        return web.Response(body=self.body, status=self.status, headers=self.headers)

    class Schema(schemas.Schema):
        expected_method = schemas.fields.String(required=True,
                                                validate=schemas.validate.OneOf(['GET', 'HEAD', 'OPTIONS', 'POST',
                                                                                 'PUT', 'PATCH', 'DELETE', 'TRACE',
                                                                                 'CONNECT']))
        expected_path = schemas.fields.String(required=True, validate=schemas.validate.Length(min=1, max=2048))
        expected_headers = schemas.fields.Dict(keys=schemas.fields.String(validate=[schemas.validate.Length(1, 256),
                                                                                    schemas.validate.Regexp(r'^[\w-]+$')]),
                                               values=schemas.fields.String(validate=schemas.validate.Length(1, 256)))
        expected_body = schemas.fields.String(validate=schemas.validate.Length(min=1, max=65536), allow_none=True)
        expected_body_bytes = schemafields.Base64Field()

        status = schemas.fields.Integer(validate=schemas.validate.Range(100, 599))
        headers = schemas.fields.Dict(keys=schemas.fields.String(validate=[schemas.validate.Length(1, 256),
                                                                           schemas.validate.Regexp(r'^[\w-]+$')]),
                                      values=schemas.fields.String(validate=schemas.validate.Length(1, 256)))
        body = schemas.fields.String(validate=schemas.validate.Length(min=1, max=65536))
        body_bytes = schemafields.Base64Field()

        port = schemas.fields.Integer(validate=schemas.validate.Range(0, 65535))
        timeout = schemas.fields.Integer(validate=schemas.validate.Range(1, settings.MAX_JOB_TIME))


@register_instruction
class JSONHTTPServer(HTTPServer):
    NAME = 'json-http-server'

    def __init__(self,
                 expected_method, expected_path, expected_headers=None, expected_body=None, expected_body_schema=None,
                 status=200, headers=None, body=None,
                 port=None, timeout=None):

        self.expected_body_schema = expected_body_schema

        super().__init__(expected_method=expected_method, expected_path=expected_path,
                         expected_headers=expected_headers, expected_body=expected_body,
                         status=status, headers=headers, body=body,
                         port=port, timeout=timeout)

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

    def prepare_response(self):
        return web.json_response(body=self.body, status=self.status, headers=self.headers)

    class Schema(HTTPServer.Schema):
        expected_body_schema = schemas.fields.Raw()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields['body'] = schemas.fields.Raw()
            self.fields['expected_body'] = schemas.fields.Raw(allow_none=True)

            self.fields.pop('body_bytes')
            self.fields.pop('expected_body_bytes')

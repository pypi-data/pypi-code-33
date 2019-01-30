
from json import loads

from marshmallow.schema import Schema
from marshmallow.exceptions import ValidationError

from . import json
from .context import request, context
from .decorators import decoratormethod, decoratorlist

def validation_error_to_lambda_error():
    try:
        yield
    except ValidationError as error:
        yield json.response(
            {
                'errorMessage': ', '.join(
                    f'{key}: {" ".join(value)}'
                    for key, value in error.messages.items()
                ),
                'errorType': 'ValidationError',
                'stackTrace': [],
            },
            status = 422
        )


class LambdaMixIn():

    @decoratormethod
    def lambda_handler(self, endpoint, *args, context=[], proxy_integration=False, loads=loads, **kwargs):
        """

        """

        if proxy_integration:
            raise NotImplementedError('proxy integration')

        else:
            context = decoratorlist([context])

            schema = endpoint.__annotations__.get('event')

            @context
            def parse_event():
                global context
                nonlocal loads
                context.event = loads(request.get_data())

            if isinstance(schema, Schema):
                context(validation_error_to_lambda_error)
                @context
                def validate_event(event):
                    "raises ValidationError"
                    nonlocal schema
                    schema.load(event)

            @context
            def encode_lambda_response():
                obj = yield
                yield json.response(obj)

        return self.route(endpoint, *args, context=context, **kwargs)

import json
from functools import wraps

import statsd
from jsonschema import FormatChecker, validate


def validate_with(schema_data: bytes):
    """Ensure the decorated function is called with valid arguments

    :param schema_data: The JSONSchema to validate against.
        Should be UTF-8-encoded JSON bytes.
    :type schema_data: bytes
    :return: Decorator for validating function arguments against `schema`
    """
    schema = json.loads(schema_data.decode("utf-8"))

    def validity_wrapper(f):
        @wraps(f)
        def check_validity(*args, **kwargs):
            with statsd.Timer(__name__).time("check_validity"):
                validate(kwargs, schema, format_checker=FormatChecker())
            return f(*args, **kwargs)

        return check_validity

    return validity_wrapper

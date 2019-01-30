
import json
from dataclasses import dataclass
from dataclasses_json import dataclass_json

from werkzeug.wrappers import Response

# create marshmallow schema by decorating a class
schema = lambda cls: dataclass_json(dataclass(cls)).schema()

def response(obj, **kwargs):
    return Response(
        [json.dumps(obj)],
        mimetype = 'application/json; charset=utf-8',
        **kwargs
    )

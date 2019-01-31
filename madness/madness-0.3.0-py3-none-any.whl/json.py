
import json
from dataclasses import dataclass
from dataclasses_json import dataclass_json

import madness

# create marshmallow schema by decorating a class
schema = lambda cls: dataclass_json(dataclass(cls)).schema()

def response(obj, **kwargs):
    return madness.response(
        [json.dumps(obj)],
        mimetype = 'application/json; charset=utf-8',
        **kwargs
    )

def request(*args):
    data = json.loads(madness.request.get_data())
    if args:
        return (data[arg] for arg in args)
    return data

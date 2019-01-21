import json


def serialize_to_json_string(object_to_serialize):
    class ParameterValuesEncoder(json.JSONEncoder):
        def default(self, obj):
            import inspect
            if inspect.isclass(type(obj)):
                return obj.__dict__
            return json.JSONEncoder.default(self, obj)
    return json.dumps(object_to_serialize, cls=ParameterValuesEncoder, indent=4)

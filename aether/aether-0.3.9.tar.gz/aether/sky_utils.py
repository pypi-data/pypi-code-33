import dill
import base64
from google.protobuf import json_format
import aetheruserconfig as cfg
import pyproj
import io
import json
import numpy as np
import inspect
from PIL import Image

class sky_utils(object):

    @staticmethod
    def serialize_to_bytestring(o):
        b = bytearray()
        b.extend(dill.dumps(o, protocol=2))
        return str(b)

    @staticmethod
    def deserialize_from_bytestring(s):
        return dill.loads(bytes(s))

    @staticmethod
    def serialize_for_url(o):
        return base64.urlsafe_b64encode(str(o))

    @staticmethod
    def deserialize_from_url(s):
        return base64.urlsafe_b64decode(str(s))

    @staticmethod
    def serialize_numpy(n, as_json=False):
        if as_json:
            return json.dumps(n.tolist())
        else:
            return base64.b64encode(n)

    @staticmethod
    def deserialize_numpy(s, as_json=False):
        return base64.b64decode(s)

    @staticmethod
    def serialize_pb(pb):
        return json_format.MessageToJson(pb)

    @staticmethod
    def deserialize_pb(s, pb):
        return json_format.Parse(s, pb)

    @staticmethod
    def generate_image_from_http_response(image_data):
        return Image.open(io.BytesIO(sky_utils.deserialize_from_url(image_data)))

    @staticmethod
    def is_valid_search_parameters(resource_name, query_parameters):
        allowed_query_parameters = {q.name:q for q in cfg.resources[resource_name]["_query_parameters"]}
        for p in allowed_query_parameters.values():
            if p.is_required and p.name not in query_parameters:
                return False, "Search query is missing parameter '{}'.".format(p.name)

        for name in query_parameters.keys():
            if name not in allowed_query_parameters.keys():
                return False, "Unrecognized query parameter '{}'.".format(name)

            if not allowed_query_parameters[name].is_valid_value(query_parameters[name]):
                return False, "Query parameter '{}' value is not value: {}.".format(name, query_parameters[name])
        return True, None

    @staticmethod
    def is_valid_projection(projection):
        try:
            pyproj.Proj(projection)
            return True
        except:
            return False

    @staticmethod
    def numpy_pb_to_arr(npb):
        shape = np.array(npb.shape)
        as_json = True if npb.serial_type == "json" else False
        stack = np.frombuffer(sky_utils.deserialize_numpy(npb.values, as_json=as_json), dtype=npb.dtype)
        stack = np.reshape(stack, newshape=shape)
        return stack

    @staticmethod
    def numpy_arr_to_pb(narr, npb, as_json=False):
        narr = np.copy(narr, order='C')
        npb.shape.extend(list(narr.shape))
        npb.values = sky_utils.serialize_numpy(narr, as_json=as_json)
        npb.serial_type = "json" if as_json else "bytes"
        npb.dtype = str(narr.dtype)
        return npb

    @staticmethod
    def serialize_function(func):
        s = inspect.getsource(func)
        s = base64.urlsafe_b64encode(s)
        return s


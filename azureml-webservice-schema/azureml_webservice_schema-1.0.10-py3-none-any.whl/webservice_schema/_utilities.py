# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pickle
import base64
from azureml.webservice_schema import __version__ as _sdk_version


def serialize(obj):
    serialized_bytes = pickle.dumps(obj)
    b64encoded_bytes = base64.b64encode(serialized_bytes)
    return b64encoded_bytes.decode('utf-8')


def deserialize(serialized_obj):
    obj_bytes = base64.b64decode(serialized_obj.encode('utf-8'))
    schema_obj = pickle.loads(obj_bytes)
    return schema_obj


def get_sdk_version():
    return _sdk_version

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import abc
import sys
from azureml.webservice_schema import _utilities


class InternalSchema(object):
    __metaclass__ = abc.ABCMeta

    def serialize_to_string(self):
        try:
            return _utilities.serialize(self)
        except Exception:
            raise ValueError("Failed to serialize the internal schema to string: {0}".format(sys.exc_info()[0]))

    @classmethod
    def deserialize_from_string(cls, serialized_obj):
        try:
            return _utilities.deserialize(serialized_obj)
        except Exception:
            raise ValueError("Failed to deserialize the given string {0} to an internal schema object: {1}".format(
                serialized_obj, sys.exc_info()[0]))


class Schema(object):
    def __init__(self, data_type, internal_form, swagger_form, version):
        if not isinstance(internal_form, InternalSchema):
            raise TypeError("Internal schema parameter must be specified as an instance of InternalSchema.")
        if not isinstance(swagger_form, dict):
            raise TypeError("Swagger schema parameter must be specified as a dict instance.")
        self.type = data_type
        self.internal = internal_form
        self.swagger = swagger_form
        self.version = version


class ServiceSchema(object):
    def __init__(self, inputs_schema, outputs_schema):
        if inputs_schema and not isinstance(inputs_schema, dict):
            raise TypeError("Invalid input schema parameter: must be a map of name -> Schema instance")
        if outputs_schema and not isinstance(outputs_schema, dict):
            raise TypeError("Invalid output schema parameter: must be a map of name -> Schema instance")
        self.input = inputs_schema
        self.output = outputs_schema

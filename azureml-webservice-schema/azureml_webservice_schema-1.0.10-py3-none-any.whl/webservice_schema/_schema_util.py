# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Utilities to save and load heterogeneous schema and type dictionary, also used
to parse http input using the schema and type dictionary
"""

import json
import os.path
import sys

from azureml.webservice_schema.sample_definition import SampleDefinition
from azureml.webservice_schema.schema_exceptions.client_side_exception import BadRequestException
from azureml.webservice_schema.schema_exceptions.server_side_exception import InternalServerException
from azureml.webservice_schema._schema_objects import Schema
from azureml.webservice_schema._schema_objects import ServiceSchema
from azureml.webservice_schema.data_types import DataTypes
from azureml.webservice_schema._utilities import get_sdk_version


def save_service_schema(file_path, input_schema_sample=None, output_schema_sample=None):
    if file_path is None or len(file_path) == 0:
        raise ValueError("A file path for the schema must be specified")
    target_dir = os.path.dirname(file_path)
    if len(target_dir) > 0 and not os.path.exists(target_dir):
        raise ValueError("Please specify a valid path to save the schema file to")
    if input_schema_sample is None and output_schema_sample is None:
        raise ValueError("At least one of the input / output schema samples need to be specified on this call")

    result_dict = _generate_service_schema(input_schema_sample, output_schema_sample)

    try:
        with open(file_path, 'w') as outfile:
            json.dump(result_dict, outfile)
    except Exception:
        print("Failed to save schema file")
        raise


def _generate_service_schema(input_schema_sample=None, output_schema_sample=None):
    result = {}
    for key, sample in [('input', input_schema_sample), ('output', output_schema_sample)]:
        if sample is not None:
            if not isinstance(sample, dict):
                raise ValueError('Invalid {0} schema sample: must be a map {0} '
                                 'name -> {0} definition'.format(key))
            result[key] = _get_serialized_schema_dict(sample)
    return result


def load_service_schema(filename):
    if filename is None:
        raise TypeError('A filename must be specified.')
    if not os.path.exists(filename):
        raise ValueError('Specified schema file cannot be found: {}.'.format(filename))
    with open(filename, 'r') as outfile:
        schema_document = json.load(outfile)

    input_schema = None
    if "input" in schema_document:
        input_schema = _get_deserialized_schema_dict(schema_document["input"])
    output_schema = None
    if "output" in schema_document:
        output_schema = _get_deserialized_schema_dict(schema_document["output"])

    return ServiceSchema(input_schema, output_schema)


def _validate_inputs(input_dict, schema):
    if type(input_dict) != dict:
        raise BadRequestException("Input request does not respect the schema defined "
                                  "by the service's swagger specification.")
    # because schema does not currently track whether an input is required or not,
    # we can only validate if there are extra arguments at this point
    for key in input_dict:
        if key not in schema:
            raise BadRequestException("Argument mismatch: Unexpected "
                                      "argument {0}".format(key))


def parse_service_input(http_body, service_input_schema):
    if service_input_schema is None:
        raise InternalServerException("service schema is set to None")
    try:
        input_json = json.loads(http_body)
    except Exception:
        raise BadRequestException('Input failed JSON deserialization: {}'.format(sys.exc_info()[0]))
    run_input = dict()
    _validate_inputs(input_json, service_input_schema)
    for input_name, raw_input_value in input_json.items():
        input_schema = service_input_schema[input_name]
        if isinstance(input_schema, Schema):
            try:
                if input_schema.type is DataTypes.NUMPY:
                    from azureml.webservice_schema._numpy_util import NumpyUtil
                    parsed_input_value = NumpyUtil.get_input_object(raw_input_value, input_schema)
                elif input_schema.type is DataTypes.SPARK:
                    from azureml.webservice_schema._spark_util import SparkUtil
                    parsed_input_value = SparkUtil.get_input_object(raw_input_value, input_schema)
                elif input_schema.type is DataTypes.PANDAS:
                    from azureml.webservice_schema._pandas_util import PandasUtil
                    parsed_input_value = PandasUtil.get_input_object(raw_input_value, input_schema)
                elif input_schema.type is DataTypes.STANDARD:
                    from azureml.webservice_schema._python_util import PythonUtil
                    parsed_input_value = PythonUtil.get_input_object(raw_input_value, input_schema)
                else:
                    raise ValueError("Invalid schema type found: {}. Only types defined in dataTypes.DataTypes are "
                                     "valid".format(input_schema.type))
                run_input[input_name] = parsed_input_value
            except (ValueError, TypeError) as ex:
                schema_version_string = input_schema.version
                raise BadRequestException("Failed to deserialize {} to type provided by input schema, Error Details: "
                                          "{}. Installed SDK version: {}. Loaded schema version:"
                                          " {}".format(input_name, str(ex), get_sdk_version(), schema_version_string))
            except Exception:
                schema_version_string = input_schema.version
                raise InternalServerException("Unexpected error occurred when parsing the input named {} with value"
                                              " {}: {}. Installed SDK version: {}. Loaded schema version:"
                                              " {}".format(input_name, raw_input_value, sys.exc_info()[0],
                                                           get_sdk_version(), schema_version_string))
        else:
            raise InternalServerException("Unexpected error occurred: Invalid schema object found for input name {}. "
                                          "Expected an instance of the Schema class. Installed SDK version: {}."
                                          .format(input_name, get_sdk_version()))
    return run_input


def parse_batch_input(input_file, input_schema, has_header):
    try:
        if input_schema.type is DataTypes.NUMPY:
            from azureml.webservice_schema._numpy_util import NumpyUtil
            parsed_input_value = NumpyUtil.get_input_object_from_file(input_file, input_schema, has_header)
        elif input_schema.type is DataTypes.SPARK:
            from azureml.webservice_schema._spark_util import SparkUtil
            parsed_input_value = SparkUtil.get_input_object_from_file(input_file, input_schema, has_header)
        elif input_schema.type is DataTypes.PANDAS:
            from azureml.webservice_schema._pandas_util import PandasUtil
            parsed_input_value = PandasUtil.get_input_object_from_file(input_file, input_schema)
        elif input_schema.type is DataTypes.STANDARD:
            from azureml.webservice_schema._python_util import PythonUtil
            parsed_input_value = PythonUtil.get_input_object_from_file(input_file, input_schema)
        else:
            raise ValueError("Invalid schema type found: {}. Only types defined in dataTypes.DataTypes are "
                             "valid".format(input_schema.type))
    except ValueError as ex:
        raise BadRequestException("Failed to deserialize {0} to type provided by input schema, Error Details: "
                                  "{1}".format(input_file, str(ex)))
    return parsed_input_value


def _get_serialized_schema_dict(schema):
    if schema is None:
        return
    result = dict()
    for input_key, input_value in schema.items():
        if isinstance(input_value, SampleDefinition):
            result[input_key] = input_value.serialize()
        else:
            raise ValueError("Invalid Schema: Bad input type detected for argument {0}, input schema only supports "
                             "types or Sample Definition objects, found {1}".format(input_key, type(input_value)))
    return result


def _get_deserialized_schema_dict(schema):
    result = dict()
    for input_key, input_value in schema.items():
        if "type" not in input_value or input_value["type"] is None:
            raise ValueError("Invalid schema, type not found for item {0}".format(input_key))
        if "internal" not in input_value or input_value["internal"] is None:
            raise ValueError("Invalid schema, internal schema not found for item {0}".format(input_key))
        if "swagger" not in input_value or input_value["swagger"] is None:
            raise ValueError("Invalid schema, swagger not found for item {0}".format(input_key))

        schema_version = input_value["version"]
        serialized_schema = input_value["internal"]
        data_type = input_value["type"]
        if data_type is DataTypes.NUMPY:
            from azureml.webservice_schema._numpy_util import NumpySchema
            internal_schema = NumpySchema.deserialize_from_string(serialized_schema)
        elif data_type is DataTypes.SPARK:
            from azureml.webservice_schema._spark_util import SparkSchema
            internal_schema = SparkSchema.deserialize_from_string(serialized_schema)
        elif data_type is DataTypes.PANDAS:
            from azureml.webservice_schema._pandas_util import PandasSchema
            internal_schema = PandasSchema.deserialize_from_string(serialized_schema)
        elif data_type is DataTypes.STANDARD:
            from azureml.webservice_schema._python_util import PythonSchema
            internal_schema = PythonSchema.deserialize_from_string(serialized_schema)
        else:
            raise ValueError("Invalid schema type found: {}. Only types defined in dataTypes.DataTypes are "
                             "valid".format(data_type))
        result[input_key] = Schema(data_type, internal_schema, input_value["swagger"], schema_version)
    return result

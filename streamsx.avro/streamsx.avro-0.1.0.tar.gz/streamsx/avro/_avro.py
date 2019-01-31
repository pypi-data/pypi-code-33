# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2019

import os
from tempfile import mkstemp
import streamsx.spl.op
import streamsx.spl.types
from streamsx.topology.schema import CommonSchema, StreamSchema
from streamsx.spl.types import rstring



AvroStreamSchema = StreamSchema('tuple<blob binary>')
"""Structured schema containing the message in Avro format.

``'tuple<blob binary>'``
"""

def _add_avro_message_schema_file(topology, message_schema):
    if os.path.isfile(message_schema):
        path = message_schema
    else:
        fd, path = mkstemp(suffix='.json', prefix='avsc', text=True)
        with open(fd, 'w') as tmpfile:
            tmpfile.write(message_schema)
    # add to application dir in bundle
    topology.add_file_dependency(path, 'etc')
    filename = os.path.basename(path)
    return 'etc/'+filename

def json_to_avro(stream, message_schema, name=None):
    """Converts JSON strings into binary Avro messages.

    Args:
        stream(Stream): Stream of tuples containing the JSON records. Supports ``CommonSchema.Json`` as input.
        message_schema(str|file): Avro schema to serialize the Avro message from JSON input.
        name(str): Operator name in the Streams context, defaults to a generated name.

    Returns:
        Output Stream with schema :py:const:`~streamsx.avro.AvroStreamSchema` (Avro records in binary format).
    """

    _op = _JSONToAvro(stream, schema=AvroStreamSchema, name=name)
    _op.params['avroMessageSchemaFile'] = _op.expression('getApplicationDir()+"/'+_add_avro_message_schema_file(stream.topology, message_schema)+'"')
    return _op.outputs[0]


def avro_to_json(stream, message_schema, name=None):
    """Converts binary Avro messages to JSON strings.

    Args:
        stream(Stream): Stream of tuples containing the binary Avro records.
        message_schema(str|file): Avro schema to deserialize the binary Avro message to JSON.
        name(str): Operator name in the Streams context, defaults to a generated name.

    Returns:
        Output Stream with schema :py:const:`~CommonSchema.Json`.
    """

    _op = _AvroToJSON(stream, schema=CommonSchema.Json, name=name)
    _op.params['avroMessageSchemaFile'] = _op.expression('getApplicationDir()+"/'+_add_avro_message_schema_file(stream.topology, message_schema)+'"')
    return _op.outputs[0]


class _AvroToJSON(streamsx.spl.op.Invoke):
    def __init__(self, stream, schema, avroKeySchemaFile=None, avroMessageSchemaFile=None, inputAvroKey=None, inputAvroMessage=None, outputJsonKey=None, outputJsonMessage=None, vmArg=None, name=None):
        topology = stream.topology
        kind="com.ibm.streamsx.avro::AvroToJSON"
        inputs=stream
        schemas=schema
        params = dict()
        if vmArg is not None:
            params['vmArg'] = vmArg
        if avroKeySchemaFile is not None:
            params['avroKeySchemaFile'] = avroKeySchemaFile
        if avroMessageSchemaFile is not None:
            params['avroMessageSchemaFile'] = avroMessageSchemaFile
        if inputAvroKey is not None:
            params['inputAvroKey'] = inputAvroKey
        if inputAvroMessage is not None:
            params['inputAvroMessage'] = inputAvroMessage
        if outputJsonKey is not None:
            params['outputJsonKey'] = outputJsonKey
        if outputJsonMessage is not None:
            params['outputJsonMessage'] = outputJsonMessage

        super(_AvroToJSON, self).__init__(topology,kind,inputs,schema,params,name)


class _JSONToAvro(streamsx.spl.op.Invoke):
    def __init__(self, stream, schema, avroMessageSchemaFile=None, bytesPerMessage=None, embedAvroSchema=None, ignoreParsingError=None, inputJsonMessage=None, outputAvroMessage=None, submitOnPunct=None, timePerMessage=None, tuplesPerMessage=None, vmArg=None, name=None):
        topology = stream.topology
        kind="com.ibm.streamsx.avro::JSONToAvro"
        inputs=stream
        schemas=schema
        params = dict()
        if vmArg is not None:
            params['vmArg'] = vmArg
        if avroMessageSchemaFile is not None:
            params['avroMessageSchemaFile'] = avroMessageSchemaFile
        if bytesPerMessage is not None:
            params['bytesPerMessage'] = bytesPerMessage
        if embedAvroSchema is not None:
            params['embedAvroSchema'] = embedAvroSchema
        if ignoreParsingError is not None:
            params['ignoreParsingError'] = ignoreParsingError
        if inputJsonMessage is not None:
            params['inputJsonMessage'] = inputJsonMessage
        if outputAvroMessage is not None:
            params['outputAvroMessage'] = outputAvroMessage
        if submitOnPunct is not None:
            params['submitOnPunct'] = submitOnPunct
        if timePerMessage is not None:
            params['timePerMessage'] = timePerMessage
        if tuplesPerMessage is not None:
            params['tuplesPerMessage'] = tuplesPerMessage

        super(_JSONToAvro, self).__init__(topology,kind,inputs,schema,params,name)


# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2019

"""
Overview
++++++++

Provides functions for serialization and deserialization of messages in an Apache Avro format.

The following transformations are supported:
 * JSON -> AVRO
 * AVRO -> JSON


This package is compatible with Streaming Analytics service on IBM Cloud:

  * `IBM Streaming Analytics <https://www.ibm.com/cloud/streaming-analytics>`_

Sample
++++++

A simple example of a Streams application that emits http requests::

    from streamsx.topology.topology import *
    from streamsx.topology.schema import CommonSchema, StreamSchema
    from streamsx.topology.context import submit
    import streamsx.avro as avro

    topo = Topology()

    s = topo.source(JsonData()).as_json()
    # convert json to avro
    binary_msg = avro.json_to_avro(s, avro_schema)
    # convert avro to json
    res = avro.avro_to_json(binary_msg, avro_schema)
    res.print()

    submit('STREAMING_ANALYTICS_SERVICE', topo)

"""

__version__='0.1.0'

__all__ = ['json_to_avro', 'avro_to_json']
from streamsx.avro._avro import json_to_avro, avro_to_json


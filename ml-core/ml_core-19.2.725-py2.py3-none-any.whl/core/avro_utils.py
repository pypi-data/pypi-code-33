# -*- coding: utf8 -*-
import six
from missinglink.core.json_utils import clean_system_keys_iter, get_json_items, MlJson as json


class AvroWriter(object):
    def __init__(self, write_to=None, key_name=None, schema=None):
        self.__key_name = key_name
        self.__write_to = write_to or six.BytesIO()
        self.__writer = None
        self.__schema_so_far = schema or {}
        self.__items_so_far = []

    @property
    def stream(self):
        return self.__write_to

    @classmethod
    def get_schema_from_item(cls, schema_so_far, item):
        type_convert = {'str': 'string', 'bool': 'boolean', 'unicode': 'string', 'int': 'long'}

        has_nulls = False
        for key, val in item.items():
            if key in schema_so_far:
                continue

            if val is None:
                has_nulls = True
                continue

            t = type(val).__name__
            t = type_convert.get(t, t)
            schema_so_far[key] = t

        return has_nulls

    @classmethod
    def __create_schema_for_fields(cls, schema_fields):
        import avro

        schema_data = {
            "namespace": "ml.data",
            "type": "record",
            "name": "Data",
            "fields": [],
        }

        for key, t in schema_fields.items():
            field_data = {'name': key, 'type': [t, 'null']}
            schema_data['fields'].append(field_data)

        parse_method = getattr(avro.schema, 'parse', None) or getattr(avro.schema, 'Parse')
        data = json.dumps(schema_data)
        return parse_method(data)

    def close(self):
        self.__write_items_so_far()

        if self.__writer is None:
            return

        self.__writer.flush()

    def __write_multi(self, items):
        for item in items:
            self.__writer.append(item)

    def __create_writer_if_needed(self, schema):
        if self.__writer is not None:
            return

        from avro.datafile import DataFileWriter
        from avro.io import DatumWriter

        avro_schema = self.__create_schema_for_fields(schema)
        self.__writer = DataFileWriter(self.__write_to, DatumWriter(), avro_schema)

    def __write_items_so_far(self):
        self.__create_writer_if_needed(self.__schema_so_far)
        self.__write_multi(self.__items_so_far)

        self.__items_so_far = []

    def __write_first_items(self, data_iter):
        if self.__writer is not None:
            return []

        has_nulls = True

        for item in data_iter:
            has_nulls = self.get_schema_from_item(self.__schema_so_far, item)

            self.__items_so_far.append(item)

            if has_nulls:
                continue

            break

        if has_nulls:
            return []

        self.__write_items_so_far()

    def __write_the_rest(self, data_iter):
        for item in data_iter:
            self.__writer.append(item)

    def append_data(self, data):
        data_iter = clean_system_keys_iter(get_json_items(data, key_name=self.__key_name))

        self.__write_first_items(data_iter)
        self.__write_the_rest(data_iter)

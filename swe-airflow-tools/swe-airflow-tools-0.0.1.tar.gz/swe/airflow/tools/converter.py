# #! -*- coding: utf-8 -*-
#
# import abc
#
# import json
#
# from tools.json import JSONEncoder
#
#
# class IConverter(metaclass=abc.ABCMeta):
#
#     @abc.abstractmethod
#     def convert(self, values):
#         """
#         Convert records/_rows for content type
#
#         :param values: records or _rows to convert
#         :type values: list, array or vector
#
#         return: dict, list, array or vector
#         """
#         raise NotImplementedError()
#
# class TupleToJSONConverter(IConverter):
#
#     def __init__(self, parent_key, fields_mapping, values=None):
#
#         self.parent_key = parent_key
#         self.fields_mapping = fields_mapping
#         self.values = values
#
#         if not self.parent_key:
#             raise Exception('Invalid parent key!')
#         if not self.fields_mapping:
#             raise Exception('Invalid fields mapping!')
#
#     def convert(self, values):
#
#         if not self.values:
#             self.values = values
#
#         new_values = {self.parent_key: []}
#
#         for i, value in enumerate(values):
#             record_dict = {}
#             for k, field in enumerate(self.fields_mapping):
#                 record_dict.update({field: value[k]})
#             new_values[self.parent_key].append(record_dict)
#
#         return json.dumps(new_values, cls=JSONEncoder)
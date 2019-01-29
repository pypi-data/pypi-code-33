# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *


class JsonConvertable:
    def to_json(self):
        raise NotImplemented()


class Framework(JsonConvertable):
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def to_json(self):
        return {
            "name": self.name,
            "version": self.version
        }


# class Platform(JsonConvertable):
#     def __init__(self, name, version):
#         self.name = name
#         self.version = version
#
#     def to_json(self):
#         return {
#             "name": self.name,
#             "version": self.version
#         }


class Artifact(JsonConvertable):
    header = ['source_uid', 'source_url', 'binding_uid', 'name', 'type', 'created',
              'frameworks', 'source_entry', 'properties', 'source_rn']

    def __init__(self, source_uid, source_url, binding_uid, name, type, created, frameworks,
                 source_entry, properties={}, source_rn=''):
        validate_type(source_uid, "source_uid", str, True)
        validate_type(source_url, "source_url", str, False)
        validate_type(binding_uid, "binding_uid", str, True)
        validate_type(name, "name", str, True)
        validate_type(type, "type", str, True)
        validate_type(created, "created", str, True)
        validate_type(frameworks, "frameworks", list, True)
        validate_type(source_entry, "source_entry", dict, False)
        validate_type(source_entry, "properties", dict, False)
        validate_type(source_rn, "source_rn", str, False)

        self.source_uid = source_uid
        self.source_url = source_url
        self.binding_uid = binding_uid
        self.name = name
        self.type = type
        self.created = created
        self.frameworks = frameworks
        self.source_entry = source_entry
        self.properties = properties
        self.source_rn = source_rn

    def to_json(self):
        j = {
            key: (self.__dict__[key] if not isinstance(self.__dict__[key], JsonConvertable) else self.__dict__[key].to_json())
            for key in self.__dict__ if not key.startswith('_')
        }

        j['frameworks'] = [f.to_json() for f in j['frameworks']]

        return j


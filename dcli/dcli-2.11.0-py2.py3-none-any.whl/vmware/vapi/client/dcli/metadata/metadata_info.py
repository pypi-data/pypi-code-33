"""
This module provides data classes for handling metadata information
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2017-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'


class CommandMetadataInfo(object):
    """
    Class exposing command metadata information
    """
    def __init__(self):
        # command identity of type CommandIdentityMetadataInfo
        self.identity = None
        self.description = ''
        self.formatter = None
        self.service_id = None
        self.operation_id = None
        # list of OptionMetadataInfo
        self.options = []
        # list of OutputMetadataInfo
        self.output_field_list = []
        self.input_definition = None
        # instance of type OperationRestMetadata
        self.rest_info = None


class CommandIdentityMetadataInfo(object):
    """
    Class representing command identity consisting of path and name
    """
    def __init__(self, path, name, short_description=None):
        self.path = path
        self.name = name
        self.short_description = short_description

    def __hash__(self):
        return hash((self.path, self.name))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.name == self.name and other.path == self.path
        return False


class OptionMetadataInfo(object):
    """
    Class holding parameter metadata information for specific command
    """
    def __init__(self):
        self.long_option = None
        self.short_option = None
        self.field_name = None
        self.description = None
        self.type = None
        self.generic = None


class OutputMetadataInfo(object):
    """
    Class holding output metadata information for a specific structure
    """
    def __init__(self):
        self.structure_id = None
        self.output_fields = None  # list of OutputFieldMetadataInfo


class OutputFieldMetadataInfo(object):
    """
    Class holding metadata information for a structure field
    """
    def __init__(self):
        self.field_name = None
        self.display_name = None


class NamespaceMetadataInfo(object):
    """
    Class representing collective point for namesapce metadata information
    """
    def __init__(self):
        # namespace identity of type
        # NamespaceIdentityMetadataInfo
        self.identity = None
        self.description = ''

        # children namespace identities of type
        # NamespaceIdentityMetadataInfo
        self.children = []


class NamespaceIdentityMetadataInfo(object):
    """
    Class representing namesapce identity consisting of path and name
    """
    def __init__(self, path, name, short_description=None):
        self.path = path
        self.name = name
        self.short_description = short_description

    def __hash__(self):
        return hash((self.path, self.name))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.name == self.name and other.path == self.path
        return False


class StructureInfo(object):
    """
    Class representing data information for structure
    """
    def __init__(self):
        self.path = None
        self.fields = None  # list of FieldInfo


class FieldInfo(object):
    """
    Class representing structure field data information
    """
    def __init__(self):
        self.name = None
        self.type = None
        self.union_case = None
        self.union_tag = None
        self.has_fields_of_struct_name = None

    def is_union_tag(self):
        """
        Checks whether the field object is union tag

        :return: True if field is union case, False otherwise
        :rtype: :class:`bool`
        """
        return self.union_tag is not None

    def is_union_case(self):
        """
        Checks whether the field object is union case

        :return: True if field is union case, False otherwise
        :rtype: :class:`bool`
        """
        return self.union_case is not None


class UnionTagInfo(object):
    """
    Class representing union tag data information
    """
    def __init__(self):
        self.name = None


class UnionCaseInfo(object):
    """
    Class representing union case data information
    """
    def __init__(self):
        self.tag_name = None
        self.list_value = None


class TypeInfo(object):
    """
    Class representing field type data information
    """
    def __init__(self):
        self.category = None  # one of BUILTIN, USER_DEFINED, or GENERIC
        self.user_defined_type = None  # populated if category is USER_DEFINED
        self.generic_instantiation = None  # populated if category is GENERIC
        self.builtin_type = None  # populated if category is BUILTIN


class UserDefinedTypeInfo(object):
    """
    Class representing user defined type info data information
    """
    def __init__(self):
        self.resource_type = None
        self.resource_id = None


class GenericInstantiationInfo(object):
    """
    Class representing generic instantiation data information
    """
    def __init__(self):
        self.generic_type = None

        # populated if generic type is either
        # optional, list, or set. It's reference to
        # TypeInfo object
        self.element_type = None


class EnumerationInfo(object):
    """
    Class representing enumeration data information
    """
    def __init__(self):
        self.name = None
        self.values = None


class OperationInfo(object):
    """
    Class representing operation data information
    """
    def __init__(self):
        self.name = None
        self.params = None  # list of FieldInfo


class OperationRestMetadata(object):
    """
    Class representing REST metadata for operation entity
    """
    def __init__(self):
        self.http_method = None
        self.url_template = None
        self.content_type = None
        self.accept_header = None
        self.request_body_field = None
        self.path_variable_map = {}
        # contains values from RequestParam
        # VMODL2 annotation
        self.request_param_map = {}
        # contains values from RequestHeader
        # VMODL2 annotation
        self.request_header_map = {}
        # contains values from
        # RequestMapping VMODL2 annotations
        self.request_mapping_params_map = {}
        # contains values from
        # RequestMapping VMODL2 annotations
        self.request_mapping_header_map = {}

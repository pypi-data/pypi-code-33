"""
This module provides concrete metadata provider implementation of the abstract
metadata provider class reading from a local file
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2017-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import os
import json
import logging
import six
from pkg_resources import resource_string
from vmware.vapi.client.dcli.metadata.abstract_metadata_provider import \
    AbstractMetadataProvider
from vmware.vapi.data.definition import (
    DynamicStructDefinition, IntegerDefinition, VoidDefinition,
    BooleanDefinition, StringDefinition, SecretDefinition, StructDefinition,
    StructRefDefinition, OptionalDefinition, ListDefinition,
    OpaqueDefinition, DoubleDefinition,
    BlobDefinition)
from vmware.vapi.client.dcli.options import CliOptions
from vmware.vapi.client.dcli.util import \
    ServerTypes, get_vmc_authentication_token, calculate_time, \
    prompt_for_credentials, get_decoded_JWT_token
from vmware.vapi.client.dcli.exceptions import handle_error
from vmware.vapi.data.serializers.cleanjson import DataValueConverter
from vmware.vapi.bindings.converter import TypeConverter, RestConverter
from vmware.vapi.client.dcli.metadata.metadata_info import OperationRestMetadata
from vmware.vapi.client.dcli.metadata import converter
from com.vmware.vapi.metadata.metamodel_client import GenericInstantiation, \
    Type, Enumeration, ElementValue
from com.vmware.vapi.std.errors_client import NotFound
from com.vmware.vapi_client import MetadataInfo

logger = logging.getLogger(__name__)


class LocalMetadataProvider(AbstractMetadataProvider):
    """
    Implementation of the :class:`vmware.vapi.client.dcli.metadata
    .abstract_metadata_provider.AbstractMetadataProvider`
    which takes metadata information from the cli metadata and metamodel vapi
    services
    """

    def __init__(self,
                 server_type=None,
                 server_url=None,
                 requests_session=None,
                 credstore=None):
        self.server_type = server_type

        self.cli_namespaces = []
        self.cli_commands = []
        self.metamodel_structures = {}
        self.metamodel_enumerations = {}
        self.metamodel_operations = {}
        self.rest_metadata = {}

        if server_type == 'internal':
            json_str, _ = LocalMetadataProvider.\
                read_local_metadata(CliOptions.DCLI_INTERNAL_COMMANDS_METADATA_FILE,
                                    'internal-commands-metadata.json')
        elif server_type in (ServerTypes.VMC, ServerTypes.NSX):
            json_str = LocalMetadataProvider.read_metadata(server_url,
                                                           server_type,
                                                           requests_session,
                                                           credstore)

        if (six.PY2 and isinstance(json_str, str)) or six.PY3:
            json_str = json_str.decode(encoding='utf-8')
        self._parse_metadata(json_str)

    @staticmethod
    def read_metadata(server_url, server_type, requests_session, credstore):
        """
        Reading VMC metadata information

        :param server_url: server url from which to fetch metadata information
        :type server_url: :class:`str`
        :param requests_session: requests session object which would make the http requests
        :type requests_session: :class: `requests.sessions.Session`
        :return: JSON string of metadata representation
        :rtype: :class:`str`
        """
        # try reading metadata from local file first if set up through env var
        if server_type == ServerTypes.VMC:
            metadata_file_env_var = 'DCLI_VMC_METADATA_FILE'
            metadata_file_from_env_var = CliOptions.DCLI_VMC_METADATA_FILE
            metadata_url = CliOptions.DCLI_VMC_METADATA_URL
            server_type_name = 'VMC'
        else:
            metadata_file_env_var = 'DCLI_NSX_METADATA_FILE'
            metadata_file_from_env_var = CliOptions.DCLI_NSX_METADATA_FILE
            metadata_url = CliOptions.DCLI_NSX_METADATA_URL
            server_type_name = 'NSX'

        json_str, file_name = LocalMetadataProvider.read_local_metadata(metadata_file_from_env_var)
        if not json_str:
            credstore_url = server_url
            if server_type == ServerTypes.NSX:
                credstore_url = CliOptions.DCLI_VMC_SERVER
            token = LocalMetadataProvider.retrieve_token(credstore_url,
                                                         server_type,
                                                         requests_session,
                                                         credstore)

            # need to preserve current adapters and revert them back once
            # we're done with caching. Otherwise caching would be switched on
            # for every further request made with requests.
            old_http_adapter = requests_session.adapters['http://']
            old_https_adapter = requests_session.adapters['https://']

            cached_session = \
                LocalMetadataProvider.get_cached_session(requests_session)

            metadata_url = metadata_url.format(server_url.rstrip('/'))
            headers = {'Authorization': 'Bearer {}'.format(token)}
            try:
                logger.info('Fetching remote %s metadata from "%s"', server_type_name, metadata_url)
                response = \
                    calculate_time(lambda:
                                   cached_session.get(metadata_url,
                                                      headers=headers),
                                   "Fetch {} metadata remotely".format(server_type_name))
                response.raise_for_status()
                json_str = response.content
            except Exception as e:
                error_msg = 'Unable to fetch metadata from {} server. ' \
                            'Error: {}'.format(server_type_name, str(e))
                handle_error(error_msg, exception=e)
                raise Exception(e)

            # swtiching caching off by mounting back old adapters
            requests_session.mount('http://', old_http_adapter)
            requests_session.mount('https://', old_https_adapter)
        else:
            logger.info('Using %s metadata provided through environment '
                        'variable %s: %s', server_type_name, metadata_file_env_var, file_name)
        return json_str

    @staticmethod
    def retrieve_token(server_url, server_type, requests_session, credstore):
        """
        From refresh token retrieves authentication access token

        :param server_url: url to use for storing credentials information for
        :type server_url: :class:`str`
        :param requests_session: requests session object which would make the http requests
        :type requests_session: :class: `requests.sessions.Session`
        :return: authentication access token
        :rtype: :class:`str`
        """
        org_id = None
        if server_type == ServerTypes.NSX:
            import re
            # searching for '/orgs/GUID' pattern in NSX URL
            match = re.search('orgs//([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})', server_url)
            if match is not None:
                org_id = match.group(1)

        refresh_token, _ = credstore.get_csp_refresh_token(server_url, org_id=org_id)
        should_save = False
        if not refresh_token:
            _, refresh_token, should_save = prompt_for_credentials(server_type, org_id=org_id)

        token = get_vmc_authentication_token(requests_session, refresh_token)

        # Save credentials after we verify they are correct;
        # That is after we get authentication token successfully
        if should_save:
            decoded_token = get_decoded_JWT_token(auth_token=token, session=requests_session)
            credstore.add(server_url, refresh_token, decoded_token["context_name"], decoded_token["username"])

        return token

    @staticmethod
    def get_cached_session(requests_session):
        """
        get cachable requests session

        :param requests_session: requests session object used to initialize
            cached session with
        :type requests_session: :class: `requests.sessions.Session`
        :return: session object
        :rtype: :class:`requests.sessions.Session`
        """
        from cachecontrol import CacheControl
        from cachecontrol.caches.file_cache import FileCache

        metadata_cache = CliOptions.DCLI_METADATA_CACHE_DIR
        if not os.path.exists(metadata_cache):
            os.makedirs(metadata_cache)
        return CacheControl(requests_session,
                            cache=FileCache(metadata_cache))

    @staticmethod
    def read_local_metadata(file_from_env_var, file_name=None):
        """
        Reads metadata info from file specified through environment variable
        or gets it from packaged metadata file
        :param file_name: File name in the package with the required metadata
        :type file_name: :class:`str`
        :param env_var: Environment variable to try to read metadata from
        :type env_var: :class:`str`
        :return: Metadata information as a string and file_name the
            metadata was read from
        :rtype: :class:`tuple` of :class:`str` and :class:`str`
        """
        try:
            json_str = None
            if file_from_env_var is not None:
                file_name = file_from_env_var
                with open(file_name) as m_file:
                    json_metadata = json.load(m_file)
                    json_str = json.dumps(json_metadata)
            elif file_name is not None:
                json_str = resource_string('vmware.vapi.client.dcli.metadata',
                                           'data/%s' % file_name)
            return json_str, file_name
        except Exception as e:
            handle_error('Error occurred while trying to read metadata from file: %s' % str(e), exception=e)
            raise e

    def get_commands(self, namespace_path=None):
        """
        Gets list of commands for the specified namespace path

        :param namespace_path: namespace path to retrieve commands from
        :type namespace_path: :class:`str`
        :return: list of commands
        :rtype: :class:`list` of
            :class:`vmware.vapi.client.dcli.metadata.metadata_info.CommandIdentityMetadataInfo`
        """
        commands = []
        for command in self.cli_commands:
            if not namespace_path or command.identity.path == namespace_path:
                commands.append(
                    converter.convert_command_identity_to_dcli_data_object(
                        command.identity, command.description))
        return commands

    def get_command_info(self, namespace_path, command_name):
        """
        Gets command metadata info by specified command name and namespace path

        :param namespace_path: namespace path to the command
        :type namespace_path: :class:`str`
        :param command_name: command name
        :type command_name: :class:`str`
        :return: coomand metdata info object
        :rtype: :class:`vmware.vapi.client.dcli.metadata.metadata_info.
                                                            CommandMetadataInfo`
        """
        result = None
        for command in self.cli_commands:
            if command.identity.path == namespace_path and \
                    command.identity.name == command_name:
                result = converter.convert_cli_command_to_dcli_data_object(
                    command)
                break

        if not result:
            raise NotFound()  # pylint: disable=W0710

        # fill in rest metadata
        try:
            operation_path = '%s.%s' % (result.service_id,
                                        result.operation_id)
            result.rest_info = self.rest_metadata[operation_path]
        except KeyError:
            result.rest_info = None

        # fill in input definition from introspection service
        try:
            result.input_definition = self.get_command_input_definition(
                result.service_id, result.operation_id)
        except NotFound:
            result.input_definition = None

        # set default formatter for nsx and skyscraper to simple
        result.formatter = 'simple'

        return result

    def get_namespaces(self):
        """
        Gets the list of namespaces

        :return: list of namespace identity objects
        :rtype: :class:`list` of type
            :class:`vmware.vapi.client.dcli.metadata.metadata_info.
                                                NamespaceIdentityMetadataInfo`
        """
        return [converter.convert_namespace_identity_to_dcli_data_object(
            namespace.identity, namespace.description)
                for namespace in self.cli_namespaces]

    def get_namespace_info(self, namespace_path, namespace_name):
        """
        Gets namesapce metadata info for specified namespace path and name

        :param namespace_path: namespace path
        :type namespace_path: :class:`str`
        :param namespace_name: namespace name
        :type namespace_name: :class:`str`
        :return: Namespace info object found by given path and name
        :rtype: :class:`vmware.vapi.client.dcli.metadata.metadata_info.NamespaceMetadataInfo`
        """
        result = None
        for namespace in self.cli_namespaces:
            if namespace.identity.path == namespace_path and \
                    namespace.identity.name == namespace_name:
                result = converter.convert_cli_namespace_to_dcli_data_object(
                    namespace)
        if result is None:
            raise NotFound()  # pylint: disable=W0710

        return result

    def get_command_input_definition(self, service_path, operation_name):
        """
        Gets vapi input definition for a command specified by path and name

        :param service_path: service path where the operation resides
        :type service_path: :class:`str`
        :param operation_name: operation name
        :type operation_name: :class:`str`
        :return: Input definition object for an operation specified by
        service path and operation name
        :rtype: :class:`vmware.vapi.data.definition.StructDefinition`
        """
        return InputDefinitionProvider(self)\
            .get_method_input_definition(service_path, operation_name)

    def get_structure_info(self, structure_path):
        """
        Gets metadata for structure specified by structure path

        :param structure_path: structure path
        :type structure_path: :class:`str`
        :return: Strucutre info object found by specified structure path
        :rtype: :class:`vmware.vapi.client.dcli.metadata.metadata_info.StructureInfo`
        """
        try:
            structure_info = self.metamodel_structures[structure_path]
        except KeyError:
            raise NotFound()  # pylint: disable=W0710

        return converter.convert_struct_from_metamodel_to_dcli_data_object(
            structure_info)

    def get_enumeration_info(self, enumeration_path):
        """
        Gets metadata for enumeration specified by enumeration path

        :param enumeration_path: enumeration path
        :type enumeration_path: :class:`str`
        :return: Enumeration info object specified by enumeration path
        :rtype: :class:`vmware.vapi.client.dcli.metadata.metadata_info.EnumerationInfo
        """
        try:
            enumeration_info = self.metamodel_enumerations[enumeration_path]
        except KeyError:
            raise NotFound()  # pylint: disable=W0710

        return converter.convert_enum_from_metamodel_to_dcli_data_object(
            enumeration_info)

    def get_operation_info(self, operation_path, operation_name):
        """
        Gets metadata for operation specified by operation path and operation
        name

        :param operation_path: operation path
        :type operation_path: :class:`str`
        :param operation_name: operation name
        :type operation_name: :class:`str`
        :return: operation info object specified by operation path and
        operation name
        :rtype: :class:`vmware.vapi.client.dcli.metadata.metadata_info.OperationInfo
        """
        operation_key = "%s.%s" % (operation_path, operation_name)
        try:
            operation_info = self.metamodel_operations[operation_key]
        except KeyError:
            raise NotFound()  # pylint: disable=W0710

        return converter.convert_operation_from_metamodel_to_dcli_data_object(
            operation_info)

    def get_authentication_schemes(self, operation_path, operation_name):
        """
        Gets authentication schema for an operation specified by operation
        path and operation name

        :param operation_path: operation path
        :type operation_path: :class:`str`
        :param operation_name: operation name
        :type operation_name: :class:`str`
        :return: authentication schema for a specified operation
        :rtype: :class:`dict` of :class:`str` and :class:`list` of :class:`str`
        """
        return {'com.vmware.vapi.std.security.user_pass': [False]}

    def _parse_metamodel_metadata(self, component_infos):
        """
        Traverses through component info objects and parse them respectively

        :param metamodel_json: json object to traverse
        :type metamodel_json: :class:`dict` of :class:`str` and :class:`dict`
        """
        for component in component_infos:
            self._parse_component(component)

    def _parse_component(self, component_info):
        """
        Parse ComponentInfo data object

        :param component_info:
            :class:`com.vmware.vapi.metadata.metamodel_provider.ComponentInfo`
        :type component_info: ComponentInfo object
        """
        for _, info in six.iteritems(component_info.packages):
            self._parse_package_info(info)

    def _parse_package_info(self, package_info):
        """
        Parse PackageInfo data

        :type  package_info:
            :class:`com.vmware.vapi.metadata.metamodel_provider.PackageInfo`
        :param package_info: PackageInfo object
        """
        self._parse_structure_data(package_info.structures)
        self._parse_enumeration_data(package_info.enumerations)
        for name, info in six.iteritems(package_info.services):
            self._parse_service_info(name, info)

    def _parse_service_info(self, service_name, service_info):
        """
        Parse ServiceInfo remote data

        :type  service_name: :class:`str`
        :param service_name: Service Name
        :type  service_info: :class:
        `com.vmware.vapi.metadata.metamodel_provider.ServiceInfo`
        :param service_info: ServiceInfo object
        """
        self._parse_structure_data(service_info.structures)
        self._parse_enumeration_data(service_info.enumerations)
        for name, info in six.iteritems(service_info.operations):
            full_operation_name = "%s.%s" % (service_name,
                                             name)
            self.metamodel_operations[full_operation_name] = info
            rest_md = OperationRestMetadata()
            for param in info.params:
                self._parse_common_metadata_info(param.metadata)
                self._parse_operation_param_rest_metadata(param.name,
                                                          param.metadata,
                                                          rest_md)
            self._parse_common_metadata_info(info.output.metadata)
            self._parse_operation_rest_metadata(info.metadata, rest_md)
            self.rest_metadata[full_operation_name] = rest_md

    def _parse_structure_data(self, structure_info):
        """
        Parse remote StructureData

        :type  structure_info: :class:`dict` or
            :class:`str`, :class:`com.vmware.vapi.metadata.metamodel.StructureInfo`
        :param structure_info: StructureData Map
        """
        for name, info in six.iteritems(structure_info):
            self._parse_enumeration_data(info.enumerations)
            for field in info.fields:
                self._parse_common_metadata_info(field.metadata)
            self.metamodel_structures[name] = info

    def _parse_enumeration_data(self, enumeration_data):
        """
        Parse remote EnumerationData

        :type  source_id: :class:`str`
        :param source_id: Source metamodel
        :type  enumeration_data: :class:`dict` of
            :class:`str`, :class:`com.vmware.vapi.metadata.metamodel.EnumerationInfo`
        :param enumeration_data: EnumerationData Map
        """
        for name, info in six.iteritems(enumeration_data):
            self.metamodel_enumerations[name] = info

    def _parse_common_metadata_info(self, metadata):
        """
        Parse remote metadata
        """
        pass
        # if 'Resource' in metadata:
        #     elements = metadata['Resource'].elements
        #     if 'value' in elements:
        #         value = elements['value']
        #         if value.type == ElementValue.Type.STRING:
        #             self._maps.resource_mapping.setdefault(
        #                 source_id, set()).add(value.string_value)
        #         elif value.type == ElementValue.Type.STRING_LIST:
        #             self._maps.resource_mapping.setdefault(
        #                 source_id, set()).update(value.list_value)

    def _parse_operation_rest_metadata(self, metadata, rest_md):  # pylint: disable=R0201
        """
        Collects rest metadata annotations for an operation

        :param metadata: operation's metadata coming from metamodel
        :type metadata: :class:`dict` of :class:`str` and
            :class:`com.vmware.vapi.metadata.metamodel_client.ElementMap`
        :param rest_md: dcli rest data container
        :type rest_md: :class:vmware.vapi.client.dcli.metadata.metadata_info
            .OperationRestMetadata
        """
        if not metadata:
            return

        if 'RequestMapping' in metadata:
            elements = metadata['RequestMapping'].elements
            if 'value' in elements:
                value = elements['value']
                if value.type == ElementValue.Type.STRING:
                    rest_md.url_template = value.string_value
            if 'method' in elements:
                method = elements['method']
                if method.type == ElementValue.Type.STRING:
                    rest_md.http_method = method.string_value
            if 'contentType' in elements:
                content_type = elements['contentType']
                if content_type.type == ElementValue.Type.STRING:
                    rest_md.content_type = content_type.string_value
            if 'accept' in elements:
                accept_header = elements['accept']
                if accept_header.type == ElementValue.Type.STRING:
                    rest_md.accept_header = accept_header.string_value
            if 'params' in elements:
                params = elements['params']
                if params.type == ElementValue.Type.STRING:
                    param, value = params.string_value.split('=')
                    rest_md.request_mapping_params_map[param] = value
                elif params.type == ElementValue.Type.STRING_LIST:
                    for item in params.list_value:
                        param, value = item.split('=')
                        rest_md.request_mapping_params_map[param] = value
            if 'headers' in elements:
                headers = elements['headers']
                if headers.type == ElementValue.Type.STRING:
                    param, value = params.string_value.split('=')
                    rest_md.request_mapping_header_map[param] = value
                elif headers.type == ElementValue.Type.STRING_LIST:
                    for item in headers.list_value:
                        param, value = item.split('=')
                        rest_md.request_mapping_header_map[param] = value

    def _parse_operation_param_rest_metadata(self, param_name, metadata, rest_md):  # pylint: disable=R0201
        """
        Collects rest metadata annotations for an operation's parameter

        :param param_name: Name of the parameter
        :type param_name: :class:`str`
        :param metadata: parameter's metadata coming from metamodel
        :type metadata: :class:`dict` of :class:`str` and
            :class:`com.vmware.vapi.metadata.metamodel_client.ElementMap`
        :param rest_md: dcli rest data container
        :type rest_md: :class:`vmware.vapi.client.dcli.metadata.metadata_info
            .OperationRestMetadata`
        """
        if not metadata:
            return

        if 'PathVariable' in metadata:
            elements = metadata['PathVariable'].elements
            if 'value' in elements:
                value = elements['value']
                if value.type == ElementValue.Type.STRING:
                    rest_md.path_variable_map[param_name] = value.string_value
        if 'RequestParam' in metadata:
            elements = metadata['RequestParam'].elements
            if 'value' in elements:
                value = elements['value']
                if value.type == ElementValue.Type.STRING:
                    rest_md.request_param_map[param_name] = value.string_value
        if 'RequestHeader' in metadata:
            elements = metadata['RequestHeader'].elements
            if 'value' in elements:
                value = elements['value']
                if value.type == ElementValue.Type.STRING:
                    rest_md.request_header_map[param_name] = value.string_value
        if 'RequestBody' in metadata:
            elements = metadata['RequestBody'].elements
            if 'value' in elements:
                value = elements['value']
                if value.type == ElementValue.Type.STRING:
                    rest_md.request_body_field = param_name

    def _parse_cli_metadata(self, cli_component_info):
        """
        Traverses through cli component info objects and maps all cli
        namespaces and commands

        :param cli_json: json object to traverse
        :type cli_json: :class:`dict` of :class:`str` and :class:`dict`
        """
        for component in cli_component_info:
            self.cli_namespaces.extend(component.namespaces)
            self.cli_commands.extend(component.commands)

    def _parse_metadata(self, metadata_json_str):
        """
        Parses metadata from given json string in clean-json format as it
        builds dictionaries by collecting various needed data

        :param metadata_json_str: json string to parse
        :type metadata_json_str: :class:`str`
        """
        try:
            mi_binding_type = MetadataInfo.get_binding_type()
            data_value = DataValueConverter.convert_to_data_value(metadata_json_str)
            metadata_info = TypeConverter.convert_to_python(data_value,
                                                            mi_binding_type,
                                                            rest_converter_mode=RestConverter.VAPI_REST)

            metamodel_component_infos = []
            cli_component_infos = []

            metadata = metadata_info.metadata
            for info_id in metadata:
                info = metadata[info_id]
                metamodel_component_infos.append(info.metamodel)
                cli_component_infos.append(info.cli)

            self._parse_metamodel_metadata(metamodel_component_infos)
            self._parse_cli_metadata(cli_component_infos)
        except Exception as e:
            err_msg = 'Error occurred while trying to process metadata from ' \
                      'json file'
            handle_error(err_msg, exception=e)
            raise e


class InputDefinitionProvider(object):
    """
    Helper class for building method definitions from metamodel information
    """
    builtin_type_map = {
        Type.BuiltinType.BINARY: BlobDefinition,
        Type.BuiltinType.BOOLEAN: BooleanDefinition,
        Type.BuiltinType.DATE_TIME: StringDefinition,
        Type.BuiltinType.DOUBLE: DoubleDefinition,
        Type.BuiltinType.ID: StringDefinition,
        Type.BuiltinType.LONG: IntegerDefinition,
        Type.BuiltinType.OPAQUE: OpaqueDefinition,
        Type.BuiltinType.SECRET: SecretDefinition,
        Type.BuiltinType.STRING: StringDefinition,
        Type.BuiltinType.DYNAMIC_STRUCTURE: DynamicStructDefinition,
        Type.BuiltinType.URI: StringDefinition,
        Type.BuiltinType.VOID: VoidDefinition,
    }

    def __init__(self, local_metadata_provider):
        self.local_metadata_provider = local_metadata_provider

    def get_method_input_definition(self, service_name, operation_name):
        """
        Returns method definition for specified operation

        :param service_name: name of the service the operation resides in
        :type service_name: :class:`str`
        :param operation_name: name of the operation, part of the service
        specified in the constructor
        :type operation_name: :class:`str`

        :return: method definition of the specified operation
        :rtype: :class:`vmware.vapi.core.MethodDefinition`
        """
        operation_key = '%s.%s' % (service_name, operation_name)
        try:
            op_info = self.local_metadata_provider.metamodel_operations[
                operation_key]
        except KeyError:
            raise NotFound()  # pylint: disable=W0710

        return self._get_method_input_def(op_info)

    def _get_method_input_def(self, op_info):
        """
        Returns method definition object

        :param op_info: metamodel operation info object
        :type op_info: :class:`com.vmware.vapi.metadata.metamodel_client
        .OperationInfo`

        :return: method definition of the specified operation
        :rtype: :class:`vmware.vapi.core.MethodDefinition`
        """
        param_list = []
        for field_info in op_info.params:
            param_list.append((field_info.name, self._get_type_info(
                field_info.type)))
        return StructDefinition('operation-input', param_list)

    def _get_structure_info(self, struct_name, struct_info, visited_structs):
        """
        Returns structure definition object

        :param struct_name: full structure name
        :type struct_name: :class:`str`
        :param struct_info: metamodel structure info object
        :type struct_info: :class:`com.vmware.vapi.metadata.metamodel_client
        .StructureInfo`
        :param visited_structs: list of already visited structures.
        Needed to handle recursive references.
        :type visited_structs: :class:`list` of :class:`str`

        :return: Structure definition for the specified structure
        :rtype: :class:`vmware.vapi.data.definition.StructDefinition`
        """
        visited_structs.append(struct_name)
        fields = []
        for field_info in struct_info.fields:
            field_name = None
            if self.local_metadata_provider.server_type in (ServerTypes.VMC,
                                                            ServerTypes.NSX):
                try:
                    field_name = field_info.metadata[
                        'SerializationName'].elements['value'].string_value
                except Exception:
                    raise Exception('Unable to get serialization name for %s '
                                    'field' % field_info.name)
            else:
                field_name = field_info.name

            if field_name is None:
                raise ValueError("Couldn't find the serialization name for "
                                 'field %s' % field_info.name)

            fields.append((field_name, self._get_type_info(
                field_info.type, visited_structs)))
        visited_structs.pop()
        return StructDefinition(name=struct_name, fields=fields)

    def _get_type_info(self, type_info, visited_structs=None):
        """
        Returns type definition object

        :param type_info: metamodel type info object
        :type type_info: :class:`com.vmware.vapi.metadata.metamodel_client.Type`
        :param visited_structs: list of already visited structures.
        Needed to handle recursive references.
        :type visited_structs: :class:`list` of :class:`str`

        :return: Type definition of the specified type
        :rtype: :class:`vmware.vapi.data.definition.DataDefinition`
        """
        if visited_structs is None:
            visited_structs = []
        if type_info.category == Type.Category.BUILTIN:
            return InputDefinitionProvider.builtin_type_map[
                type_info.builtin_type]()
        elif type_info.category == Type.Category.GENERIC:
            return self._get_generic_type_info(
                type_info.generic_instantiation, visited_structs)
        # Userdefined type
        return self._get_user_defined_type_info(type_info, visited_structs)

    def _get_generic_type_info(self, generic_instantiation, visited_structs):
        """
        Returns generic definition object

        :param generic_instantiation: metamodel generic info object
        :type generic_instantiation:
        :class:`com.vmware.vapi.metadata.metamodel_client.GenericInstantiation`
        :param visited_structs: list of already visited structures.
        Needed to handle recursive references.
        :type visited_structs: :class:`list` of :class:`str`

        :return: input definition for the specified generic
        :rtype: :class:`vmware.vapi.data.definition.DataDefinition`
        """
        if generic_instantiation.generic_type in [
                GenericInstantiation.GenericType.LIST,
                GenericInstantiation.GenericType.SET]:
            return ListDefinition(self._get_type_info(
                generic_instantiation.element_type, visited_structs))
        elif generic_instantiation.generic_type == \
                GenericInstantiation.GenericType.OPTIONAL:
            return OptionalDefinition(self._get_type_info(
                generic_instantiation.element_type, visited_structs))

        # Map type
        key_def = self._get_type_info(generic_instantiation.map_key_type,
                                      visited_structs)
        value_def = self._get_type_info(
            generic_instantiation.map_value_type, visited_structs)
        fields = [('key', key_def),
                  ('value', value_def)]
        # generate correct name for the struct

        return ListDefinition(StructDefinition(name='map_entry',
                                               fields=fields))

    def _get_user_defined_type_info(self, type_info, visited_structs):
        """
        Returns user definition object

        :param type_info: metamodel type info object
        :type type_info: :class:`com.vmware.vapi.metadata.metamodel_client.Type`
        :param visited_structs: list of already visited structures.
        Needed to handle recursive references.
        :type visited_structs: :class:`list` of :class:`str`

        :return: input definition for the specified user defined type
        :rtype: :class:`vmware.vapi.data.definition.DataDefinition`
        """
        if type_info.user_defined_type.resource_type == \
                Enumeration.RESOURCE_TYPE:
            return StringDefinition()

        # Structure reference
        struct_full_name = type_info.user_defined_type.resource_id
        if struct_full_name in visited_structs:
            return StructRefDefinition(struct_full_name)

        try:
            struct_info = \
                self.local_metadata_provider.metamodel_structures[
                    struct_full_name]
        except NotFound as e:
            handle_error("Input definition error: Structure info for "
                         "'%s' was not found" % struct_full_name, exception=e)
            raise e  # pylint: disable=W0710
        return self._get_structure_info(struct_full_name,
                                        struct_info, visited_structs)

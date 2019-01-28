"""
This module provides concrete json-rpc provider of the abstract metadata
provider class
"""

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2017-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import logging
from vmware.vapi.client.dcli.metadata.abstract_metadata_provider import \
    AbstractMetadataProvider
from vmware.vapi.data.serializers.introspection import \
    convert_data_value_to_data_def
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from vmware.vapi.client.dcli.metadata import converter
from com.vmware.vapi.std.introspection_client import Operation as \
    IntrospectionOperation
from com.vmware.vapi.metadata.cli_client import (Command, Namespace)
from com.vmware.vapi.metadata.authentication_client import \
    (Package, Service, AuthenticationInfo)
from com.vmware.vapi.metadata.authentication.service_client import Operation \
    as AuthenticationOperation
from com.vmware.vapi.metadata.metamodel_client import (
    Enumeration, Structure)
from com.vmware.vapi.metadata.metamodel.service_client import Operation as \
    MetamodelOperation
from com.vmware.vapi.std.errors_client import NotFound, OperationNotFound

logger = logging.getLogger(__name__)


class RemoteMetadataProvider(AbstractMetadataProvider):
    """
    Implementation of the :class:`vmware.vapi.client.dcli.metadata
    .abstract_metadata_provider.AbstractMetadataProvider`
    which takes metadata information from the cli metadata and metamodel vapi
    services
    """

    def __init__(self, connector):
        self.stub_config = StubConfigurationFactory.new_std_configuration(
            connector)

        # cli metadata stubs
        self.cmd_instance_stub = Command(self.stub_config)
        self.ns_instance_stub = Namespace(self.stub_config)

        # introspection stubs
        self.introspection_operation_stub = \
            IntrospectionOperation(self.stub_config)

        # metamodel stubs
        self.structure_stub = Structure(self.stub_config)
        self.enumeration_stub = Enumeration(self.stub_config)
        self.metamodel_operation_stub = MetamodelOperation(self.stub_config)

        # authentication stubs
        self.authentication_package_stub = Package(self.stub_config)
        self.authentication_service_stub = Service(self.stub_config)
        self.authentication_operation_stub = \
            AuthenticationOperation(self.stub_config)

    def get_commands(self, namespace_path=None):
        """
        Gets list of commands for the specified namespace path

        :param namespace_path: namespace path to retrieve commands from
        :type namespace_path: :class:`str`
        :return: list of commands
        :rtype: :class:`list` of
            :class:`vmware.vapi.client.dcli.metadata.metadata_info.CommandIdentityMetadataInfo`
        """
        return [converter.convert_command_identity_to_dcli_data_object(
            cmd_identity)
                for cmd_identity in self.cmd_instance_stub.list(namespace_path)]

    def get_command_info(self, namespace_path, command_name):
        """
        Gets command metadata info by specified command name and namespace path

        :param namespace_path: namespace path to the command
        :type namespace_path: :class:`str`
        :param command_name: command name
        :type command_name: :class:`str`
        :return: coomand metdata info object
        :rtype: :class:`vmware.vapi.client.dcli.metadata.metadata_info.CommandMetadataInfo`
        """
        cmd_id = Command.Identity(path=namespace_path, name=command_name)
        cli_metadata_cmd = self.cmd_instance_stub.get(identity=cmd_id)
        result = converter.convert_cli_command_to_dcli_data_object(
            cli_metadata_cmd)

        # fill in input definition from introspection service
        try:
            result.input_definition = self.get_command_input_definition(
                result.service_id, result.operation_id)
        except NotFound:
            logger.error("Introspection information was not found for "
                         "operation '%s' in service '%s'", command_name, namespace_path)
            result.input_definition = None

        return result

    def get_namespaces(self):
        """
        Gets the list of namespaces

        :return: list of namespace identity objects
        :rtype: :class:`list` of type
            :class:`vmware.vapi.client.dcli.metadata.metadata_info.NamespaceIdentityMetadataInfo`
        """
        return [converter.convert_namespace_identity_to_dcli_data_object(
            ns_identity)
                for ns_identity in self.ns_instance_stub.list()]

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
        ns_id = Namespace.Identity(path=namespace_path, name=namespace_name)
        cli_metadata_ns = self.ns_instance_stub.get(identity=ns_id)
        result = converter.convert_cli_namespace_to_dcli_data_object(
            cli_metadata_ns)
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
        method_info = self.introspection_operation_stub.get(
            service_id=service_path,
            operation_id=operation_name)
        return convert_data_value_to_data_def(
            method_info.input_definition.get_struct_value())

    def get_structure_info(self, structure_path):
        """
        Gets metadata for structure specified by structure path

        :param structure_path: structure path
        :type structure_path: :class:`str`
        :return: Strucutre info object found by specified structure path
        :rtype: :class:`vmware.vapi.client.dcli.metadata.metadata_info.StructureInfo`
        """
        metamodel_struct_info = self.structure_stub.get(structure_path)
        return converter.convert_struct_from_metamodel_to_dcli_data_object(
            metamodel_struct_info)

    def get_enumeration_info(self, enumeration_path):
        """
        Gets metadata for enumeration specified by enumeration path

        :param enumeration_path: enumeration path
        :type enumeration_path: :class:`str`
        :return: Enumeration info object specified by enumeration path
        :rtype: :class:`vmware.vapi.client.dcli.metadata.metadata_info.EnumerationInfo
        """
        metamodel_enum_info = self.enumeration_stub.get(enumeration_path)
        return converter.convert_enum_from_metamodel_to_dcli_data_object(
            metamodel_enum_info)

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
        metamodel_operation_info = self.metamodel_operation_stub.get(
            operation_path, operation_name)
        return \
            converter.convert_operation_from_metamodel_to_dcli_data_object(
                metamodel_operation_info)

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
        auth_schemas = {}
        self._get_authentication_schemes_internal(auth_schemas,
                                                  operation_path,
                                                  operation_name,
                                                  False)
        return auth_schemas

    def _get_authentication_schemes_internal(self,
                                             auth_schemes,
                                             path,
                                             cmd,
                                             is_session_aware):
        """
        Method to get valid authentication schemes for a given vAPI command

        :type  auth_schemes: :class:`map`
        :param auth_schemes: Authentication scheme and scheme type
        :type  path: :class:`str`
        :param path: vAPI command path
        :type  cmd: :class:`str`
        :param cmd: vAPI command name
        :type  is_session_aware: :class:`bool`
        :param is_session_aware: Is authentication scheme type session aware
        """
        schemes = []
        try:
            operation_info = \
                self.authentication_operation_stub.get(path, cmd)
            schemes = operation_info.schemes
        except NotFound:
            # if this call came through session aware try login method
            # instead of create
            # XXX remove this code once everyone moves over to create/delete
            # methods
            if is_session_aware and cmd == 'create':
                self._get_authentication_schemes_internal(auth_schemes, path, 'login', True)
                return
        except OperationNotFound:
            return

        if not schemes:
            try:
                service_info = \
                    self.authentication_service_stub.get(path)
                schemes = service_info.schemes
            except NotFound:
                pass

            while not schemes and path.find('.') != -1:
                pkg_name = path.rsplit('.', 1)[0]
                try:
                    package_info = \
                        self.authentication_package_stub.get(pkg_name)
                    schemes = package_info.schemes
                    path = pkg_name
                except NotFound:
                    path = pkg_name

        for scheme in schemes:
            if scheme.scheme_type == AuthenticationInfo.SchemeType.SESSIONLESS:
                # if the call came from SessionAware scheme type store
                # session manager path
                auth_schemes.setdefault(scheme.scheme, [])\
                    .append(path if is_session_aware else None)
            elif scheme.scheme_type == \
                    AuthenticationInfo.SchemeType.SESSION_AWARE:
                # In case of SessionAware we need to find the authentication
                # scheme of the login method of the session manager
                self._get_authentication_schemes_internal(auth_schemes,
                                                          scheme.session_manager, 'create', True)

# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class FunctionApp(pulumi.CustomResource):
    app_service_plan_id: pulumi.Output[str]
    """
    The ID of the App Service Plan within which to create this Function App. Changing this forces a new resource to be created.
    """
    app_settings: pulumi.Output[dict]
    """
    A key-value pair of App Settings.
    """
    client_affinity_enabled: pulumi.Output[bool]
    """
    Should the Function App send session affinity cookies, which route client requests in the same session to the same instance?
    """
    connection_strings: pulumi.Output[list]
    """
    An `connection_string` block as defined below.
    """
    default_hostname: pulumi.Output[str]
    """
    The default hostname associated with the Function App - such as `mysite.azurewebsites.net`
    """
    enable_builtin_logging: pulumi.Output[bool]
    """
    Should the built-in logging of this Function App be enabled? Defaults to `true`.
    """
    enabled: pulumi.Output[bool]
    """
    Is the Function App enabled?
    """
    https_only: pulumi.Output[bool]
    """
    Can the Function App only be accessed via HTTPS? Defaults to `false`.
    """
    identity: pulumi.Output[dict]
    """
    An `identity` block as defined below.
    """
    location: pulumi.Output[str]
    """
    Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
    """
    name: pulumi.Output[str]
    """
    The name of the Connection String.
    """
    outbound_ip_addresses: pulumi.Output[str]
    """
    A comma separated list of outbound IP addresses - such as `52.23.25.3,52.143.43.12`
    """
    resource_group_name: pulumi.Output[str]
    """
    The name of the resource group in which to create the Function App.
    """
    site_config: pulumi.Output[dict]
    """
    A `site_config` object as defined below.
    """
    site_credential: pulumi.Output[dict]
    """
    A `site_credential` block as defined below, which contains the site-level credentials used to publish to this App Service.
    """
    storage_connection_string: pulumi.Output[str]
    """
    The connection string of the backend storage account which will be used by this Function App (such as the dashboard, logs).
    """
    tags: pulumi.Output[dict]
    """
    A mapping of tags to assign to the resource.
    """
    version: pulumi.Output[str]
    """
    The runtime version associated with the Function App. Defaults to `~1`.
    """
    def __init__(__self__, __name__, __opts__=None, app_service_plan_id=None, app_settings=None, client_affinity_enabled=None, connection_strings=None, enable_builtin_logging=None, enabled=None, https_only=None, identity=None, location=None, name=None, resource_group_name=None, site_config=None, storage_connection_string=None, tags=None, version=None):
        """
        Manages a Function App.
        
        
        :param str __name__: The name of the resource.
        :param pulumi.ResourceOptions __opts__: Options for the resource.
        :param pulumi.Input[str] app_service_plan_id: The ID of the App Service Plan within which to create this Function App. Changing this forces a new resource to be created.
        :param pulumi.Input[dict] app_settings: A key-value pair of App Settings.
        :param pulumi.Input[bool] client_affinity_enabled: Should the Function App send session affinity cookies, which route client requests in the same session to the same instance?
        :param pulumi.Input[list] connection_strings: An `connection_string` block as defined below.
        :param pulumi.Input[bool] enable_builtin_logging: Should the built-in logging of this Function App be enabled? Defaults to `true`.
        :param pulumi.Input[bool] enabled: Is the Function App enabled?
        :param pulumi.Input[bool] https_only: Can the Function App only be accessed via HTTPS? Defaults to `false`.
        :param pulumi.Input[dict] identity: An `identity` block as defined below.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: The name of the Connection String.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the Function App.
        :param pulumi.Input[dict] site_config: A `site_config` object as defined below.
        :param pulumi.Input[str] storage_connection_string: The connection string of the backend storage account which will be used by this Function App (such as the dashboard, logs).
        :param pulumi.Input[dict] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[str] version: The runtime version associated with the Function App. Defaults to `~1`.
        """
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        if not app_service_plan_id:
            raise TypeError('Missing required property app_service_plan_id')
        __props__['app_service_plan_id'] = app_service_plan_id

        __props__['app_settings'] = app_settings

        __props__['client_affinity_enabled'] = client_affinity_enabled

        __props__['connection_strings'] = connection_strings

        __props__['enable_builtin_logging'] = enable_builtin_logging

        __props__['enabled'] = enabled

        __props__['https_only'] = https_only

        __props__['identity'] = identity

        if not location:
            raise TypeError('Missing required property location')
        __props__['location'] = location

        __props__['name'] = name

        if not resource_group_name:
            raise TypeError('Missing required property resource_group_name')
        __props__['resource_group_name'] = resource_group_name

        __props__['site_config'] = site_config

        if not storage_connection_string:
            raise TypeError('Missing required property storage_connection_string')
        __props__['storage_connection_string'] = storage_connection_string

        __props__['tags'] = tags

        __props__['version'] = version

        __props__['default_hostname'] = None
        __props__['outbound_ip_addresses'] = None
        __props__['site_credential'] = None

        super(FunctionApp, __self__).__init__(
            'azure:appservice/functionApp:FunctionApp',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


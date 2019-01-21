# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class GetAppServiceResult(object):
    """
    A collection of values returned by getAppService.
    """
    def __init__(__self__, app_service_plan_id=None, app_settings=None, client_affinity_enabled=None, connection_strings=None, default_site_hostname=None, enabled=None, https_only=None, location=None, outbound_ip_addresses=None, possible_outbound_ip_addresses=None, site_config=None, site_credentials=None, source_controls=None, tags=None, id=None):
        if app_service_plan_id and not isinstance(app_service_plan_id, str):
            raise TypeError('Expected argument app_service_plan_id to be a str')
        __self__.app_service_plan_id = app_service_plan_id
        """
        The ID of the App Service Plan within which the App Service exists.
        """
        if app_settings and not isinstance(app_settings, dict):
            raise TypeError('Expected argument app_settings to be a dict')
        __self__.app_settings = app_settings
        """
        A key-value pair of App Settings for the App Service.
        """
        if client_affinity_enabled and not isinstance(client_affinity_enabled, bool):
            raise TypeError('Expected argument client_affinity_enabled to be a bool')
        __self__.client_affinity_enabled = client_affinity_enabled
        """
        Does the App Service send session affinity cookies, which route client requests in the same session to the same instance?
        """
        if connection_strings and not isinstance(connection_strings, list):
            raise TypeError('Expected argument connection_strings to be a list')
        __self__.connection_strings = connection_strings
        """
        An `connection_string` block as defined below.
        """
        if default_site_hostname and not isinstance(default_site_hostname, str):
            raise TypeError('Expected argument default_site_hostname to be a str')
        __self__.default_site_hostname = default_site_hostname
        if enabled and not isinstance(enabled, bool):
            raise TypeError('Expected argument enabled to be a bool')
        __self__.enabled = enabled
        """
        Is the App Service Enabled?
        """
        if https_only and not isinstance(https_only, bool):
            raise TypeError('Expected argument https_only to be a bool')
        __self__.https_only = https_only
        """
        Can the App Service only be accessed via HTTPS?
        """
        if location and not isinstance(location, str):
            raise TypeError('Expected argument location to be a str')
        __self__.location = location
        """
        The Azure location where the App Service exists.
        """
        if outbound_ip_addresses and not isinstance(outbound_ip_addresses, str):
            raise TypeError('Expected argument outbound_ip_addresses to be a str')
        __self__.outbound_ip_addresses = outbound_ip_addresses
        """
        A comma separated list of outbound IP addresses - such as `52.23.25.3,52.143.43.12`
        """
        if possible_outbound_ip_addresses and not isinstance(possible_outbound_ip_addresses, str):
            raise TypeError('Expected argument possible_outbound_ip_addresses to be a str')
        __self__.possible_outbound_ip_addresses = possible_outbound_ip_addresses
        """
        A comma separated list of outbound IP addresses - such as `52.23.25.3,52.143.43.12,52.143.43.17` - not all of which are necessarily in use. Superset of `outbound_ip_addresses`.
        """
        if site_config and not isinstance(site_config, dict):
            raise TypeError('Expected argument site_config to be a dict')
        __self__.site_config = site_config
        """
        A `site_config` block as defined below.
        """
        if site_credentials and not isinstance(site_credentials, list):
            raise TypeError('Expected argument site_credentials to be a list')
        __self__.site_credentials = site_credentials
        if source_controls and not isinstance(source_controls, list):
            raise TypeError('Expected argument source_controls to be a list')
        __self__.source_controls = source_controls
        if tags and not isinstance(tags, dict):
            raise TypeError('Expected argument tags to be a dict')
        __self__.tags = tags
        """
        A mapping of tags to assign to the resource.
        """
        if id and not isinstance(id, str):
            raise TypeError('Expected argument id to be a str')
        __self__.id = id
        """
        id is the provider-assigned unique ID for this managed resource.
        """

async def get_app_service(name=None, resource_group_name=None, site_config=None):
    """
    Use this data source to access information about an existing App Service.
    """
    __args__ = dict()

    __args__['name'] = name
    __args__['resourceGroupName'] = resource_group_name
    __args__['siteConfig'] = site_config
    __ret__ = await pulumi.runtime.invoke('azure:appservice/getAppService:getAppService', __args__)

    return GetAppServiceResult(
        app_service_plan_id=__ret__.get('appServicePlanId'),
        app_settings=__ret__.get('appSettings'),
        client_affinity_enabled=__ret__.get('clientAffinityEnabled'),
        connection_strings=__ret__.get('connectionStrings'),
        default_site_hostname=__ret__.get('defaultSiteHostname'),
        enabled=__ret__.get('enabled'),
        https_only=__ret__.get('httpsOnly'),
        location=__ret__.get('location'),
        outbound_ip_addresses=__ret__.get('outboundIpAddresses'),
        possible_outbound_ip_addresses=__ret__.get('possibleOutboundIpAddresses'),
        site_config=__ret__.get('siteConfig'),
        site_credentials=__ret__.get('siteCredentials'),
        source_controls=__ret__.get('sourceControls'),
        tags=__ret__.get('tags'),
        id=__ret__.get('id'))

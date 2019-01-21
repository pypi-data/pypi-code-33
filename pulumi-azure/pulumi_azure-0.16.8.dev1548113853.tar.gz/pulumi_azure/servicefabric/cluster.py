# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class Cluster(pulumi.CustomResource):
    add_on_features: pulumi.Output[list]
    """
    A List of one or more features which should be enabled, such as `DnsService`.
    """
    azure_active_directory: pulumi.Output[dict]
    """
    An `azure_active_directory` block as defined below. Changing this forces a new resource to be created.
    """
    certificate: pulumi.Output[dict]
    """
    A `certificate` block as defined below.
    """
    client_certificate_thumbprints: pulumi.Output[list]
    """
    One or two `client_certificate_thumbprint` blocks as defined below.
    """
    cluster_code_version: pulumi.Output[str]
    """
    Required if Upgrade Mode set to `Manual`, Specifies the Version of the Cluster Code of the cluster.
    """
    cluster_endpoint: pulumi.Output[str]
    """
    The Cluster Endpoint for this Service Fabric Cluster.
    """
    diagnostics_config: pulumi.Output[dict]
    """
    A `diagnostics_config` block as defined below. Changing this forces a new resource to be created.
    """
    fabric_settings: pulumi.Output[list]
    """
    One or more `fabric_settings` blocks as defined below.
    """
    location: pulumi.Output[str]
    """
    Specifies the Azure Region where the Service Fabric Cluster should exist. Changing this forces a new resource to be created.
    """
    management_endpoint: pulumi.Output[str]
    """
    Specifies the Management Endpoint of the cluster such as `http://example.com`. Changing this forces a new resource to be created.
    """
    name: pulumi.Output[str]
    """
    The name of the Service Fabric Cluster. Changing this forces a new resource to be created.
    """
    node_types: pulumi.Output[list]
    """
    One or more `node_type` blocks as defined below.
    """
    reliability_level: pulumi.Output[str]
    """
    Specifies the Reliability Level of the Cluster. Possible values include `None`, `Bronze`, `Silver`, `Gold` and `Platinum`.
    """
    resource_group_name: pulumi.Output[str]
    """
    The name of the Resource Group in which the Service Fabric Cluster exists. Changing this forces a new resource to be created.
    """
    reverse_proxy_certificate: pulumi.Output[dict]
    """
    A `reverse_proxy_certificate` block as defined below.
    """
    tags: pulumi.Output[dict]
    """
    A mapping of tags to assign to the resource.
    """
    upgrade_mode: pulumi.Output[str]
    """
    Specifies the Upgrade Mode of the cluster. Possible values are `Automatic` or `Manual`.
    """
    vm_image: pulumi.Output[str]
    """
    Specifies the Image expected for the Service Fabric Cluster, such as `Windows`. Changing this forces a new resource to be created.
    """
    def __init__(__self__, __name__, __opts__=None, add_on_features=None, azure_active_directory=None, certificate=None, client_certificate_thumbprints=None, cluster_code_version=None, diagnostics_config=None, fabric_settings=None, location=None, management_endpoint=None, name=None, node_types=None, reliability_level=None, resource_group_name=None, reverse_proxy_certificate=None, tags=None, upgrade_mode=None, vm_image=None):
        """
        Manage a Service Fabric Cluster.
        
        
        :param str __name__: The name of the resource.
        :param pulumi.ResourceOptions __opts__: Options for the resource.
        :param pulumi.Input[list] add_on_features: A List of one or more features which should be enabled, such as `DnsService`.
        :param pulumi.Input[dict] azure_active_directory: An `azure_active_directory` block as defined below. Changing this forces a new resource to be created.
        :param pulumi.Input[dict] certificate: A `certificate` block as defined below.
        :param pulumi.Input[list] client_certificate_thumbprints: One or two `client_certificate_thumbprint` blocks as defined below.
        :param pulumi.Input[str] cluster_code_version: Required if Upgrade Mode set to `Manual`, Specifies the Version of the Cluster Code of the cluster.
        :param pulumi.Input[dict] diagnostics_config: A `diagnostics_config` block as defined below. Changing this forces a new resource to be created.
        :param pulumi.Input[list] fabric_settings: One or more `fabric_settings` blocks as defined below.
        :param pulumi.Input[str] location: Specifies the Azure Region where the Service Fabric Cluster should exist. Changing this forces a new resource to be created.
        :param pulumi.Input[str] management_endpoint: Specifies the Management Endpoint of the cluster such as `http://example.com`. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: The name of the Service Fabric Cluster. Changing this forces a new resource to be created.
        :param pulumi.Input[list] node_types: One or more `node_type` blocks as defined below.
        :param pulumi.Input[str] reliability_level: Specifies the Reliability Level of the Cluster. Possible values include `None`, `Bronze`, `Silver`, `Gold` and `Platinum`.
        :param pulumi.Input[str] resource_group_name: The name of the Resource Group in which the Service Fabric Cluster exists. Changing this forces a new resource to be created.
        :param pulumi.Input[dict] reverse_proxy_certificate: A `reverse_proxy_certificate` block as defined below.
        :param pulumi.Input[dict] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[str] upgrade_mode: Specifies the Upgrade Mode of the cluster. Possible values are `Automatic` or `Manual`.
        :param pulumi.Input[str] vm_image: Specifies the Image expected for the Service Fabric Cluster, such as `Windows`. Changing this forces a new resource to be created.
        """
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        __props__['add_on_features'] = add_on_features

        __props__['azure_active_directory'] = azure_active_directory

        __props__['certificate'] = certificate

        __props__['client_certificate_thumbprints'] = client_certificate_thumbprints

        __props__['cluster_code_version'] = cluster_code_version

        __props__['diagnostics_config'] = diagnostics_config

        __props__['fabric_settings'] = fabric_settings

        if not location:
            raise TypeError('Missing required property location')
        __props__['location'] = location

        if not management_endpoint:
            raise TypeError('Missing required property management_endpoint')
        __props__['management_endpoint'] = management_endpoint

        __props__['name'] = name

        if not node_types:
            raise TypeError('Missing required property node_types')
        __props__['node_types'] = node_types

        if not reliability_level:
            raise TypeError('Missing required property reliability_level')
        __props__['reliability_level'] = reliability_level

        if not resource_group_name:
            raise TypeError('Missing required property resource_group_name')
        __props__['resource_group_name'] = resource_group_name

        __props__['reverse_proxy_certificate'] = reverse_proxy_certificate

        __props__['tags'] = tags

        if not upgrade_mode:
            raise TypeError('Missing required property upgrade_mode')
        __props__['upgrade_mode'] = upgrade_mode

        if not vm_image:
            raise TypeError('Missing required property vm_image')
        __props__['vm_image'] = vm_image

        __props__['cluster_endpoint'] = None

        super(Cluster, __self__).__init__(
            'azure:servicefabric/cluster:Cluster',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


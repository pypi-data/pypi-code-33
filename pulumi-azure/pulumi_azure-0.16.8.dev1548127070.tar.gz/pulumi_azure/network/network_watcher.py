# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class NetworkWatcher(pulumi.CustomResource):
    location: pulumi.Output[str]
    """
    Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
    """
    name: pulumi.Output[str]
    """
    The name of the Network Watcher. Changing this forces a new resource to be created.
    """
    resource_group_name: pulumi.Output[str]
    """
    The name of the resource group in which to create the Network Watcher. Changing this forces a new resource to be created.
    """
    tags: pulumi.Output[dict]
    """
    A mapping of tags to assign to the resource.
    """
    def __init__(__self__, __name__, __opts__=None, location=None, name=None, resource_group_name=None, tags=None):
        """
        Manages a Network Watcher.
        
        
        :param str __name__: The name of the resource.
        :param pulumi.ResourceOptions __opts__: Options for the resource.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: The name of the Network Watcher. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the Network Watcher. Changing this forces a new resource to be created.
        :param pulumi.Input[dict] tags: A mapping of tags to assign to the resource.
        """
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        if not location:
            raise TypeError('Missing required property location')
        __props__['location'] = location

        __props__['name'] = name

        if not resource_group_name:
            raise TypeError('Missing required property resource_group_name')
        __props__['resource_group_name'] = resource_group_name

        __props__['tags'] = tags

        super(NetworkWatcher, __self__).__init__(
            'azure:network/networkWatcher:NetworkWatcher',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


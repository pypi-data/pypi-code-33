# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class EventHub(pulumi.CustomResource):
    capture_description: pulumi.Output[dict]
    """
    A `capture_description` block as defined below.
    """
    location: pulumi.Output[str]
    message_retention: pulumi.Output[int]
    """
    Specifies the number of days to retain the events for this Event Hub. Needs to be between 1 and 7 days; or 1 day when using a Basic SKU for the parent EventHub Namespace.
    """
    name: pulumi.Output[str]
    """
    Specifies the name of the EventHub Namespace resource. Changing this forces a new resource to be created.
    """
    namespace_name: pulumi.Output[str]
    """
    Specifies the name of the EventHub Namespace. Changing this forces a new resource to be created.
    """
    partition_count: pulumi.Output[int]
    """
    Specifies the current number of shards on the Event Hub. Changing this forces a new resource to be created.
    """
    partition_ids: pulumi.Output[list]
    """
    The identifiers for partitions created for Event Hubs.
    """
    resource_group_name: pulumi.Output[str]
    """
    The name of the resource group in which the EventHub's parent Namespace exists. Changing this forces a new resource to be created.
    """
    def __init__(__self__, __name__, __opts__=None, capture_description=None, location=None, message_retention=None, name=None, namespace_name=None, partition_count=None, resource_group_name=None):
        """
        Manages a Event Hubs as a nested resource within a Event Hubs namespace.
        
        
        :param str __name__: The name of the resource.
        :param pulumi.ResourceOptions __opts__: Options for the resource.
        :param pulumi.Input[dict] capture_description: A `capture_description` block as defined below.
        :param pulumi.Input[str] location
        :param pulumi.Input[int] message_retention: Specifies the number of days to retain the events for this Event Hub. Needs to be between 1 and 7 days; or 1 day when using a Basic SKU for the parent EventHub Namespace.
        :param pulumi.Input[str] name: Specifies the name of the EventHub Namespace resource. Changing this forces a new resource to be created.
        :param pulumi.Input[str] namespace_name: Specifies the name of the EventHub Namespace. Changing this forces a new resource to be created.
        :param pulumi.Input[int] partition_count: Specifies the current number of shards on the Event Hub. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which the EventHub's parent Namespace exists. Changing this forces a new resource to be created.
        """
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        __props__['capture_description'] = capture_description

        __props__['location'] = location

        if not message_retention:
            raise TypeError('Missing required property message_retention')
        __props__['message_retention'] = message_retention

        __props__['name'] = name

        if not namespace_name:
            raise TypeError('Missing required property namespace_name')
        __props__['namespace_name'] = namespace_name

        if not partition_count:
            raise TypeError('Missing required property partition_count')
        __props__['partition_count'] = partition_count

        if not resource_group_name:
            raise TypeError('Missing required property resource_group_name')
        __props__['resource_group_name'] = resource_group_name

        __props__['partition_ids'] = None

        super(EventHub, __self__).__init__(
            'azure:eventhub/eventHub:EventHub',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class PacketCapture(pulumi.CustomResource):
    filters: pulumi.Output[list]
    """
    One or more `filter` blocks as defined below. Changing this forces a new resource to be created.
    """
    maximum_bytes_per_packet: pulumi.Output[int]
    """
    The number of bytes captured per packet. The remaining bytes are truncated. Defaults to `0` (Entire Packet Captured). Changing this forces a new resource to be created.
    """
    maximum_bytes_per_session: pulumi.Output[int]
    """
    Maximum size of the capture in Bytes. Defaults to `1073741824` (1GB). Changing this forces a new resource to be created.
    """
    maximum_capture_duration: pulumi.Output[int]
    """
    The maximum duration of the capture session in seconds. Defaults to `18000` (5 hours). Changing this forces a new resource to be created.
    """
    name: pulumi.Output[str]
    """
    The name to use for this Packet Capture. Changing this forces a new resource to be created.
    """
    network_watcher_name: pulumi.Output[str]
    """
    The name of the Network Watcher. Changing this forces a new resource to be created.
    """
    resource_group_name: pulumi.Output[str]
    """
    The name of the resource group in which the Network Watcher exists. Changing this forces a new resource to be created.
    """
    storage_location: pulumi.Output[dict]
    """
    A `storage_location` block as defined below. Changing this forces a new resource to be created.
    """
    target_resource_id: pulumi.Output[str]
    """
    The ID of the Resource to capture packets from. Changing this forces a new resource to be created.
    """
    def __init__(__self__, __name__, __opts__=None, filters=None, maximum_bytes_per_packet=None, maximum_bytes_per_session=None, maximum_capture_duration=None, name=None, network_watcher_name=None, resource_group_name=None, storage_location=None, target_resource_id=None):
        """
        Configures Packet Capturing against a Virtual Machine using a Network Watcher.
        
        
        :param str __name__: The name of the resource.
        :param pulumi.ResourceOptions __opts__: Options for the resource.
        :param pulumi.Input[list] filters: One or more `filter` blocks as defined below. Changing this forces a new resource to be created.
        :param pulumi.Input[int] maximum_bytes_per_packet: The number of bytes captured per packet. The remaining bytes are truncated. Defaults to `0` (Entire Packet Captured). Changing this forces a new resource to be created.
        :param pulumi.Input[int] maximum_bytes_per_session: Maximum size of the capture in Bytes. Defaults to `1073741824` (1GB). Changing this forces a new resource to be created.
        :param pulumi.Input[int] maximum_capture_duration: The maximum duration of the capture session in seconds. Defaults to `18000` (5 hours). Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: The name to use for this Packet Capture. Changing this forces a new resource to be created.
        :param pulumi.Input[str] network_watcher_name: The name of the Network Watcher. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which the Network Watcher exists. Changing this forces a new resource to be created.
        :param pulumi.Input[dict] storage_location: A `storage_location` block as defined below. Changing this forces a new resource to be created.
        :param pulumi.Input[str] target_resource_id: The ID of the Resource to capture packets from. Changing this forces a new resource to be created.
        """
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        __props__['filters'] = filters

        __props__['maximum_bytes_per_packet'] = maximum_bytes_per_packet

        __props__['maximum_bytes_per_session'] = maximum_bytes_per_session

        __props__['maximum_capture_duration'] = maximum_capture_duration

        __props__['name'] = name

        if not network_watcher_name:
            raise TypeError('Missing required property network_watcher_name')
        __props__['network_watcher_name'] = network_watcher_name

        if not resource_group_name:
            raise TypeError('Missing required property resource_group_name')
        __props__['resource_group_name'] = resource_group_name

        if not storage_location:
            raise TypeError('Missing required property storage_location')
        __props__['storage_location'] = storage_location

        if not target_resource_id:
            raise TypeError('Missing required property target_resource_id')
        __props__['target_resource_id'] = target_resource_id

        super(PacketCapture, __self__).__init__(
            'azure:network/packetCapture:PacketCapture',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


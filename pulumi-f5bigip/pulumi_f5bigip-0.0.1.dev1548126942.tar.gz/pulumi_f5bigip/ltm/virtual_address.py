# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import pulumi
import pulumi.runtime
from .. import utilities, tables

class VirtualAddress(pulumi.CustomResource):
    def __init__(__self__, __name__, __opts__=None, advertize_route=None, arp=None, auto_delete=None, conn_limit=None, enabled=None, icmp_echo=None, name=None, traffic_group=None):
        """Create a VirtualAddress resource with the given unique name, props, and options."""
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        __props__['advertize_route'] = advertize_route

        __props__['arp'] = arp

        __props__['auto_delete'] = auto_delete

        __props__['conn_limit'] = conn_limit

        __props__['enabled'] = enabled

        __props__['icmp_echo'] = icmp_echo

        if not name:
            raise TypeError('Missing required property name')
        __props__['name'] = name

        __props__['traffic_group'] = traffic_group

        super(VirtualAddress, __self__).__init__(
            'f5bigip:ltm/virtualAddress:VirtualAddress',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


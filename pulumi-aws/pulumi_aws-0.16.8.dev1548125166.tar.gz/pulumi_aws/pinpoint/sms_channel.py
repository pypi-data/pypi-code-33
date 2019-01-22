# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class SmsChannel(pulumi.CustomResource):
    application_id: pulumi.Output[str]
    enabled: pulumi.Output[bool]
    promotional_messages_per_second: pulumi.Output[int]
    sender_id: pulumi.Output[str]
    short_code: pulumi.Output[str]
    transactional_messages_per_second: pulumi.Output[int]
    def __init__(__self__, __name__, __opts__=None, application_id=None, enabled=None, sender_id=None, short_code=None):
        """
        Create a SmsChannel resource with the given unique name, props, and options.
        
        :param str __name__: The name of the resource.
        :param pulumi.ResourceOptions __opts__: Options for the resource.
        :param pulumi.Input[str] application_id
        :param pulumi.Input[bool] enabled
        :param pulumi.Input[str] sender_id
        :param pulumi.Input[str] short_code
        """
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        if not application_id:
            raise TypeError('Missing required property application_id')
        __props__['application_id'] = application_id

        __props__['enabled'] = enabled

        __props__['sender_id'] = sender_id

        __props__['short_code'] = short_code

        __props__['promotional_messages_per_second'] = None
        __props__['transactional_messages_per_second'] = None

        super(SmsChannel, __self__).__init__(
            'aws:pinpoint/smsChannel:SmsChannel',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


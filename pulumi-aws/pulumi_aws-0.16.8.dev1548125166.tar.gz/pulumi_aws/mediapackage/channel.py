# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class Channel(pulumi.CustomResource):
    arn: pulumi.Output[str]
    """
    The ARN of the channel
    """
    channel_id: pulumi.Output[str]
    """
    A unique identifier describing the channel
    """
    description: pulumi.Output[str]
    """
    A description of the channel
    """
    hls_ingests: pulumi.Output[list]
    """
    A single item list of HLS ingest information
    """
    def __init__(__self__, __name__, __opts__=None, channel_id=None, description=None):
        """
        Provides an AWS Elemental MediaPackage Channel.
        
        
        :param str __name__: The name of the resource.
        :param pulumi.ResourceOptions __opts__: Options for the resource.
        :param pulumi.Input[str] channel_id: A unique identifier describing the channel
        :param pulumi.Input[str] description: A description of the channel
        """
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        if not channel_id:
            raise TypeError('Missing required property channel_id')
        __props__['channel_id'] = channel_id

        __props__['description'] = description

        __props__['arn'] = None
        __props__['hls_ingests'] = None

        super(Channel, __self__).__init__(
            'aws:mediapackage/channel:Channel',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


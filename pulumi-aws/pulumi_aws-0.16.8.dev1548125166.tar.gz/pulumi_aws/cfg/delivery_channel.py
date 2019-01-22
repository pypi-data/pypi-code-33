# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class DeliveryChannel(pulumi.CustomResource):
    name: pulumi.Output[str]
    """
    The name of the delivery channel. Defaults to `default`. Changing it recreates the resource.
    """
    s3_bucket_name: pulumi.Output[str]
    """
    The name of the S3 bucket used to store the configuration history.
    """
    s3_key_prefix: pulumi.Output[str]
    """
    The prefix for the specified S3 bucket.
    """
    snapshot_delivery_properties: pulumi.Output[dict]
    """
    Options for how AWS Config delivers configuration snapshots. See below
    """
    sns_topic_arn: pulumi.Output[str]
    """
    The ARN of the SNS topic that AWS Config delivers notifications to.
    """
    def __init__(__self__, __name__, __opts__=None, name=None, s3_bucket_name=None, s3_key_prefix=None, snapshot_delivery_properties=None, sns_topic_arn=None):
        """
        Provides an AWS Config Delivery Channel.
        
        > **Note:** Delivery Channel requires a [Configuration Recorder](https://www.terraform.io/docs/providers/aws/r/config_configuration_recorder.html) to be present. Use of `depends_on` (as shown below) is recommended to avoid race conditions.
        
        
        :param str __name__: The name of the resource.
        :param pulumi.ResourceOptions __opts__: Options for the resource.
        :param pulumi.Input[str] name: The name of the delivery channel. Defaults to `default`. Changing it recreates the resource.
        :param pulumi.Input[str] s3_bucket_name: The name of the S3 bucket used to store the configuration history.
        :param pulumi.Input[str] s3_key_prefix: The prefix for the specified S3 bucket.
        :param pulumi.Input[dict] snapshot_delivery_properties: Options for how AWS Config delivers configuration snapshots. See below
        :param pulumi.Input[str] sns_topic_arn: The ARN of the SNS topic that AWS Config delivers notifications to.
        """
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        __props__['name'] = name

        if not s3_bucket_name:
            raise TypeError('Missing required property s3_bucket_name')
        __props__['s3_bucket_name'] = s3_bucket_name

        __props__['s3_key_prefix'] = s3_key_prefix

        __props__['snapshot_delivery_properties'] = snapshot_delivery_properties

        __props__['sns_topic_arn'] = sns_topic_arn

        super(DeliveryChannel, __self__).__init__(
            'aws:cfg/deliveryChannel:DeliveryChannel',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


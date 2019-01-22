# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import pulumi
import pulumi.runtime
from .. import utilities, tables

class ProfileFastHttp(pulumi.CustomResource):
    def __init__(__self__, __name__, __opts__=None, connpool_maxreuse=None, connpool_maxsize=None, connpool_minsize=None, connpool_replenish=None, connpool_step=None, connpoolidle_timeoutoverride=None, defaults_from=None, forcehttp10response=None, idle_timeout=None, maxheader_size=None, name=None):
        """Create a ProfileFastHttp resource with the given unique name, props, and options."""
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        __props__['connpool_maxreuse'] = connpool_maxreuse

        __props__['connpool_maxsize'] = connpool_maxsize

        __props__['connpool_minsize'] = connpool_minsize

        __props__['connpool_replenish'] = connpool_replenish

        __props__['connpool_step'] = connpool_step

        __props__['connpoolidle_timeoutoverride'] = connpoolidle_timeoutoverride

        __props__['defaults_from'] = defaults_from

        __props__['forcehttp10response'] = forcehttp10response

        __props__['idle_timeout'] = idle_timeout

        __props__['maxheader_size'] = maxheader_size

        if not name:
            raise TypeError('Missing required property name')
        __props__['name'] = name

        super(ProfileFastHttp, __self__).__init__(
            'f5bigip:ltm/profileFastHttp:ProfileFastHttp',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


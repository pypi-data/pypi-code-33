# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import pulumi
import pulumi.runtime

class IAMPolicy(pulumi.CustomResource):
    def __init__(__self__, __name__, __opts__=None, authoritative=None, disable_project=None, policy_data=None, project=None):
        """Create a IAMPolicy resource with the given unique name, props, and options."""
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, basestring):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        if authoritative and not isinstance(authoritative, bool):
            raise TypeError('Expected property authoritative to be a bool')
        __self__.authoritative = authoritative
        __props__['authoritative'] = authoritative

        if disable_project and not isinstance(disable_project, bool):
            raise TypeError('Expected property disable_project to be a bool')
        __self__.disable_project = disable_project
        __props__['disableProject'] = disable_project

        if not policy_data:
            raise TypeError('Missing required property policy_data')
        elif not isinstance(policy_data, basestring):
            raise TypeError('Expected property policy_data to be a basestring')
        __self__.policy_data = policy_data
        __props__['policyData'] = policy_data

        if project and not isinstance(project, basestring):
            raise TypeError('Expected property project to be a basestring')
        __self__.project = project
        __props__['project'] = project

        __self__.etag = pulumi.runtime.UNKNOWN
        __self__.restore_policy = pulumi.runtime.UNKNOWN

        super(IAMPolicy, __self__).__init__(
            'gcp:projects/iAMPolicy:IAMPolicy',
            __name__,
            __props__,
            __opts__)

    def set_outputs(self, outs):
        if 'authoritative' in outs:
            self.authoritative = outs['authoritative']
        if 'disableProject' in outs:
            self.disable_project = outs['disableProject']
        if 'etag' in outs:
            self.etag = outs['etag']
        if 'policyData' in outs:
            self.policy_data = outs['policyData']
        if 'project' in outs:
            self.project = outs['project']
        if 'restorePolicy' in outs:
            self.restore_policy = outs['restorePolicy']

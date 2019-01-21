# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class SharedVPCServiceProject(pulumi.CustomResource):
    host_project: pulumi.Output[str]
    """
    The ID of a host project to associate.
    """
    service_project: pulumi.Output[str]
    """
    The ID of the project that will serve as a Shared VPC service project.
    """
    def __init__(__self__, __name__, __opts__=None, host_project=None, service_project=None):
        """
        Enables the Google Compute Engine
        [Shared VPC](https://cloud.google.com/compute/docs/shared-vpc)
        feature for a project, assigning it as a Shared VPC service project associated
        with a given host project.
        
        For more information, see,
        [the Project API documentation](https://cloud.google.com/compute/docs/reference/latest/projects),
        where the Shared VPC feature is referred to by its former name "XPN".
        
        
        :param str __name__: The name of the resource.
        :param pulumi.ResourceOptions __opts__: Options for the resource.
        :param pulumi.Input[str] host_project: The ID of a host project to associate.
        :param pulumi.Input[str] service_project: The ID of the project that will serve as a Shared VPC service project.
        """
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        if not host_project:
            raise TypeError('Missing required property host_project')
        __props__['host_project'] = host_project

        if not service_project:
            raise TypeError('Missing required property service_project')
        __props__['service_project'] = service_project

        super(SharedVPCServiceProject, __self__).__init__(
            'gcp:compute/sharedVPCServiceProject:SharedVPCServiceProject',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


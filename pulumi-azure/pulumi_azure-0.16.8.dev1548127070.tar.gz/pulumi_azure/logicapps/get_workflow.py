# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class GetWorkflowResult(object):
    """
    A collection of values returned by getWorkflow.
    """
    def __init__(__self__, access_endpoint=None, location=None, parameters=None, tags=None, workflow_schema=None, workflow_version=None, id=None):
        if access_endpoint and not isinstance(access_endpoint, str):
            raise TypeError('Expected argument access_endpoint to be a str')
        __self__.access_endpoint = access_endpoint
        """
        The Access Endpoint for the Logic App Workflow
        """
        if location and not isinstance(location, str):
            raise TypeError('Expected argument location to be a str')
        __self__.location = location
        """
        The Azure location where the Logic App Workflow exists.
        """
        if parameters and not isinstance(parameters, dict):
            raise TypeError('Expected argument parameters to be a dict')
        __self__.parameters = parameters
        """
        A map of Key-Value pairs.
        """
        if tags and not isinstance(tags, dict):
            raise TypeError('Expected argument tags to be a dict')
        __self__.tags = tags
        """
        A mapping of tags assigned to the resource.
        """
        if workflow_schema and not isinstance(workflow_schema, str):
            raise TypeError('Expected argument workflow_schema to be a str')
        __self__.workflow_schema = workflow_schema
        """
        The Schema used for this Logic App Workflow.
        """
        if workflow_version and not isinstance(workflow_version, str):
            raise TypeError('Expected argument workflow_version to be a str')
        __self__.workflow_version = workflow_version
        """
        The version of the Schema used for this Logic App Workflow. Defaults to `1.0.0.0`.
        """
        if id and not isinstance(id, str):
            raise TypeError('Expected argument id to be a str')
        __self__.id = id
        """
        id is the provider-assigned unique ID for this managed resource.
        """

async def get_workflow(name=None, resource_group_name=None):
    """
    Use this data source to access information about an existing Logic App Workflow.
    """
    __args__ = dict()

    __args__['name'] = name
    __args__['resourceGroupName'] = resource_group_name
    __ret__ = await pulumi.runtime.invoke('azure:logicapps/getWorkflow:getWorkflow', __args__)

    return GetWorkflowResult(
        access_endpoint=__ret__.get('accessEndpoint'),
        location=__ret__.get('location'),
        parameters=__ret__.get('parameters'),
        tags=__ret__.get('tags'),
        workflow_schema=__ret__.get('workflowSchema'),
        workflow_version=__ret__.get('workflowVersion'),
        id=__ret__.get('id'))

# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class GetInsightsResult(object):
    """
    A collection of values returned by getInsights.
    """
    def __init__(__self__, app_id=None, application_type=None, instrumentation_key=None, location=None, tags=None, id=None):
        if app_id and not isinstance(app_id, str):
            raise TypeError('Expected argument app_id to be a str')
        __self__.app_id = app_id
        """
        The App ID associated with this Application Insights component.
        """
        if application_type and not isinstance(application_type, str):
            raise TypeError('Expected argument application_type to be a str')
        __self__.application_type = application_type
        """
        The type of the component.
        """
        if instrumentation_key and not isinstance(instrumentation_key, str):
            raise TypeError('Expected argument instrumentation_key to be a str')
        __self__.instrumentation_key = instrumentation_key
        """
        The instrumentation key of the Application Insights component.
        """
        if location and not isinstance(location, str):
            raise TypeError('Expected argument location to be a str')
        __self__.location = location
        """
        The Azure location where the component exists.
        """
        if tags and not isinstance(tags, dict):
            raise TypeError('Expected argument tags to be a dict')
        __self__.tags = tags
        """
        Tags applied to the component.
        """
        if id and not isinstance(id, str):
            raise TypeError('Expected argument id to be a str')
        __self__.id = id
        """
        id is the provider-assigned unique ID for this managed resource.
        """

async def get_insights(name=None, resource_group_name=None):
    """
    Use this data source to access information about an existing Application Insights component.
    """
    __args__ = dict()

    __args__['name'] = name
    __args__['resourceGroupName'] = resource_group_name
    __ret__ = await pulumi.runtime.invoke('azure:appinsights/getInsights:getInsights', __args__)

    return GetInsightsResult(
        app_id=__ret__.get('appId'),
        application_type=__ret__.get('applicationType'),
        instrumentation_key=__ret__.get('instrumentationKey'),
        location=__ret__.get('location'),
        tags=__ret__.get('tags'),
        id=__ret__.get('id'))

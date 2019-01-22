# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class GetEventCategoriesResult(object):
    """
    A collection of values returned by getEventCategories.
    """
    def __init__(__self__, event_categories=None, id=None):
        if event_categories and not isinstance(event_categories, list):
            raise TypeError('Expected argument event_categories to be a list')
        __self__.event_categories = event_categories
        """
        A list of the event categories.
        """
        if id and not isinstance(id, str):
            raise TypeError('Expected argument id to be a str')
        __self__.id = id
        """
        id is the provider-assigned unique ID for this managed resource.
        """

async def get_event_categories(source_type=None):
    __args__ = dict()

    __args__['sourceType'] = source_type
    __ret__ = await pulumi.runtime.invoke('aws:rds/getEventCategories:getEventCategories', __args__)

    return GetEventCategoriesResult(
        event_categories=__ret__.get('eventCategories'),
        id=__ret__.get('id'))

# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class GetZonesResult(object):
    """
    A collection of values returned by getZones.
    """
    def __init__(__self__, names=None, project=None, id=None):
        if names and not isinstance(names, list):
            raise TypeError('Expected argument names to be a list')
        __self__.names = names
        """
        A list of zones available in the given region
        """
        if project and not isinstance(project, str):
            raise TypeError('Expected argument project to be a str')
        __self__.project = project
        if id and not isinstance(id, str):
            raise TypeError('Expected argument id to be a str')
        __self__.id = id
        """
        id is the provider-assigned unique ID for this managed resource.
        """

async def get_zones(project=None, region=None, status=None):
    """
    Provides access to available Google Compute zones in a region for a given project.
    See more about [regions and zones](https://cloud.google.com/compute/docs/regions-zones/regions-zones) in the upstream docs.
    
    ```
    data "google_compute_zones" "available" {}
    
    resource "google_compute_instance_group_manager" "foo" {
      count = "${length(data.google_compute_zones.available.names)}"
    
      name               = "terraform-test-${count.index}"
      instance_template  = "${google_compute_instance_template.foobar.self_link}"
      base_instance_name = "foobar-${count.index}"
      zone               = "${data.google_compute_zones.available.names[count.index]}"
      target_size        = 1
    }
    ```
    """
    __args__ = dict()

    __args__['project'] = project
    __args__['region'] = region
    __args__['status'] = status
    __ret__ = await pulumi.runtime.invoke('gcp:compute/getZones:getZones', __args__)

    return GetZonesResult(
        names=__ret__.get('names'),
        project=__ret__.get('project'),
        id=__ret__.get('id'))

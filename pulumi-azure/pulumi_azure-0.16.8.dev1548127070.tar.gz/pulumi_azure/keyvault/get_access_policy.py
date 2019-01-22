# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class GetAccessPolicyResult(object):
    """
    A collection of values returned by getAccessPolicy.
    """
    def __init__(__self__, certificate_permissions=None, key_permissions=None, secret_permissions=None, id=None):
        if certificate_permissions and not isinstance(certificate_permissions, list):
            raise TypeError('Expected argument certificate_permissions to be a list')
        __self__.certificate_permissions = certificate_permissions
        """
        the certificate permissions for the access policy
        """
        if key_permissions and not isinstance(key_permissions, list):
            raise TypeError('Expected argument key_permissions to be a list')
        __self__.key_permissions = key_permissions
        """
        the key permissions for the access policy
        """
        if secret_permissions and not isinstance(secret_permissions, list):
            raise TypeError('Expected argument secret_permissions to be a list')
        __self__.secret_permissions = secret_permissions
        """
        the secret permissions for the access policy
        """
        if id and not isinstance(id, str):
            raise TypeError('Expected argument id to be a str')
        __self__.id = id
        """
        id is the provider-assigned unique ID for this managed resource.
        """

async def get_access_policy(name=None):
    """
    Use this data source to access information about the permissions from the Management Key Vault Templates.
    """
    __args__ = dict()

    __args__['name'] = name
    __ret__ = await pulumi.runtime.invoke('azure:keyvault/getAccessPolicy:getAccessPolicy', __args__)

    return GetAccessPolicyResult(
        certificate_permissions=__ret__.get('certificatePermissions'),
        key_permissions=__ret__.get('keyPermissions'),
        secret_permissions=__ret__.get('secretPermissions'),
        id=__ret__.get('id'))

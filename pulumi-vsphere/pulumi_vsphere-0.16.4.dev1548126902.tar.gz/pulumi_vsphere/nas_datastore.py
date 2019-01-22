# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from . import utilities, tables

class NasDatastore(pulumi.CustomResource):
    access_mode: pulumi.Output[str]
    """
    Access mode for the mount point. Can be one of
    `readOnly` or `readWrite`. Note that `readWrite` does not necessarily mean
    that the datastore will be read-write depending on the permissions of the
    actual share. Default: `readWrite`. Forces a new resource if changed.
    """
    accessible: pulumi.Output[bool]
    """
    The connectivity status of the datastore. If this is `false`,
    some other computed attributes may be out of date.
    """
    capacity: pulumi.Output[int]
    """
    Maximum capacity of the datastore, in megabytes.
    """
    custom_attributes: pulumi.Output[dict]
    """
    Map of custom attribute ids to attribute 
    value strings to set on datasource resource. See
    [here][docs-setting-custom-attributes] for a reference on how to set values
    for custom attributes.
    """
    datastore_cluster_id: pulumi.Output[str]
    """
    The [managed object
    ID][docs-about-morefs] of a datastore cluster to put this datastore in.
    Conflicts with `folder`.
    """
    folder: pulumi.Output[str]
    """
    The relative path to a folder to put this datastore in.
    This is a path relative to the datacenter you are deploying the datastore to.
    Example: for the `dc1` datacenter, and a provided `folder` of `foo/bar`,
    Terraform will place a datastore named `terraform-test` in a datastore folder
    located at `/dc1/datastore/foo/bar`, with the final inventory path being
    `/dc1/datastore/foo/bar/terraform-test`. Conflicts with
    `datastore_cluster_id`.
    """
    free_space: pulumi.Output[int]
    """
    Available space of this datastore, in megabytes.
    """
    host_system_ids: pulumi.Output[list]
    """
    The [managed object IDs][docs-about-morefs] of
    the hosts to mount the datastore on.
    """
    maintenance_mode: pulumi.Output[str]
    """
    The current maintenance mode state of the datastore.
    """
    multiple_host_access: pulumi.Output[bool]
    """
    If `true`, more than one host in the datacenter has
    been configured with access to the datastore.
    """
    name: pulumi.Output[str]
    """
    The name of the datastore. Forces a new resource if
    changed.
    """
    protocol_endpoint: pulumi.Output[str]
    """
    Indicates that this NAS volume is a protocol endpoint.
    This field is only populated if the host supports virtual datastores.
    """
    remote_hosts: pulumi.Output[list]
    """
    The hostnames or IP addresses of the remote
    server or servers. Only one element should be present for NFS v3 but multiple
    can be present for NFS v4.1. Forces a new resource if changed.
    """
    remote_path: pulumi.Output[str]
    """
    The remote path of the mount point. Forces a new
    resource if changed.
    """
    security_type: pulumi.Output[str]
    """
    The security type to use when using NFS v4.1.
    Can be one of `AUTH_SYS`, `SEC_KRB5`, or `SEC_KRB5I`. Forces a new resource
    if changed.
    """
    tags: pulumi.Output[list]
    """
    The IDs of any tags to attach to this resource. See
    [here][docs-applying-tags] for a reference on how to apply tags.
    """
    type: pulumi.Output[str]
    """
    The type of NAS volume. Can be one of `NFS` (to denote
    v3) or `NFS41` (to denote NFS v4.1). Default: `NFS`. Forces a new resource if
    changed.
    """
    uncommitted_space: pulumi.Output[int]
    """
    Total additional storage space, in megabytes,
    potentially used by all virtual machines on this datastore.
    """
    url: pulumi.Output[str]
    """
    The unique locator for the datastore.
    """
    def __init__(__self__, __name__, __opts__=None, access_mode=None, custom_attributes=None, datastore_cluster_id=None, folder=None, host_system_ids=None, name=None, remote_hosts=None, remote_path=None, security_type=None, tags=None, type=None):
        """
        The `vsphere_nas_datastore` resource can be used to create and manage NAS
        datastores on an ESXi host or a set of hosts. The resource supports mounting
        NFS v3 and v4.1 shares to be used as datastores.
        
        > **NOTE:** Unlike [`vsphere_vmfs_datastore`][resource-vmfs-datastore], a NAS
        datastore is only mounted on the hosts you choose to mount it on. To mount on
        multiple hosts, you must specify each host that you want to add in the
        `host_system_ids` argument.
        
        [resource-vmfs-datastore]: /docs/providers/vsphere/r/vmfs_datastore.html
        
        
        :param str __name__: The name of the resource.
        :param pulumi.ResourceOptions __opts__: Options for the resource.
        :param pulumi.Input[str] access_mode: Access mode for the mount point. Can be one of
               `readOnly` or `readWrite`. Note that `readWrite` does not necessarily mean
               that the datastore will be read-write depending on the permissions of the
               actual share. Default: `readWrite`. Forces a new resource if changed.
        :param pulumi.Input[dict] custom_attributes: Map of custom attribute ids to attribute 
               value strings to set on datasource resource. See
               [here][docs-setting-custom-attributes] for a reference on how to set values
               for custom attributes.
        :param pulumi.Input[str] datastore_cluster_id: The [managed object
               ID][docs-about-morefs] of a datastore cluster to put this datastore in.
               Conflicts with `folder`.
        :param pulumi.Input[str] folder: The relative path to a folder to put this datastore in.
               This is a path relative to the datacenter you are deploying the datastore to.
               Example: for the `dc1` datacenter, and a provided `folder` of `foo/bar`,
               Terraform will place a datastore named `terraform-test` in a datastore folder
               located at `/dc1/datastore/foo/bar`, with the final inventory path being
               `/dc1/datastore/foo/bar/terraform-test`. Conflicts with
               `datastore_cluster_id`.
        :param pulumi.Input[list] host_system_ids: The [managed object IDs][docs-about-morefs] of
               the hosts to mount the datastore on.
        :param pulumi.Input[str] name: The name of the datastore. Forces a new resource if
               changed.
        :param pulumi.Input[list] remote_hosts: The hostnames or IP addresses of the remote
               server or servers. Only one element should be present for NFS v3 but multiple
               can be present for NFS v4.1. Forces a new resource if changed.
        :param pulumi.Input[str] remote_path: The remote path of the mount point. Forces a new
               resource if changed.
        :param pulumi.Input[str] security_type: The security type to use when using NFS v4.1.
               Can be one of `AUTH_SYS`, `SEC_KRB5`, or `SEC_KRB5I`. Forces a new resource
               if changed.
        :param pulumi.Input[list] tags: The IDs of any tags to attach to this resource. See
               [here][docs-applying-tags] for a reference on how to apply tags.
        :param pulumi.Input[str] type: The type of NAS volume. Can be one of `NFS` (to denote
               v3) or `NFS41` (to denote NFS v4.1). Default: `NFS`. Forces a new resource if
               changed.
        """
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        __props__['access_mode'] = access_mode

        __props__['custom_attributes'] = custom_attributes

        __props__['datastore_cluster_id'] = datastore_cluster_id

        __props__['folder'] = folder

        if not host_system_ids:
            raise TypeError('Missing required property host_system_ids')
        __props__['host_system_ids'] = host_system_ids

        __props__['name'] = name

        if not remote_hosts:
            raise TypeError('Missing required property remote_hosts')
        __props__['remote_hosts'] = remote_hosts

        if not remote_path:
            raise TypeError('Missing required property remote_path')
        __props__['remote_path'] = remote_path

        __props__['security_type'] = security_type

        __props__['tags'] = tags

        __props__['type'] = type

        __props__['accessible'] = None
        __props__['capacity'] = None
        __props__['free_space'] = None
        __props__['maintenance_mode'] = None
        __props__['multiple_host_access'] = None
        __props__['protocol_endpoint'] = None
        __props__['uncommitted_space'] = None
        __props__['url'] = None

        super(NasDatastore, __self__).__init__(
            'vsphere:index/nasDatastore:NasDatastore',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


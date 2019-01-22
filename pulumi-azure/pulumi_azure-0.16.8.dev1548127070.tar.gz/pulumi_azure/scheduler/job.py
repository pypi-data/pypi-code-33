# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class Job(pulumi.CustomResource):
    action_storage_queue: pulumi.Output[dict]
    """
    A `action_storage_queue` block defining a storage queue job action as described below. Note this is identical to an `error_action_storage_queue` block.
    """
    action_web: pulumi.Output[dict]
    """
    A `action_web` block defining the job action as described below. Note this is identical to an `error_action_web` block.
    """
    error_action_storage_queue: pulumi.Output[dict]
    """
    A `error_action_storage_queue` block defining the a web action to take on an error as described below. Note this is identical to an `action_storage_queue` block.
    """
    error_action_web: pulumi.Output[dict]
    """
    A `error_action_web` block defining the action to take on an error as described below. Note this is identical to an `action_web` block.
    """
    job_collection_name: pulumi.Output[str]
    """
    Specifies the name of the Scheduler Job Collection in which the Job should exist. Changing this forces a new resource to be created.
    """
    name: pulumi.Output[str]
    """
    The name of the Scheduler Job. Changing this forces a new resource to be created.
    """
    recurrence: pulumi.Output[dict]
    """
    A `recurrence` block defining a job occurrence schedule.
    """
    resource_group_name: pulumi.Output[str]
    """
    The name of the resource group in which to create the Scheduler Job. Changing this forces a new resource to be created.
    """
    retry: pulumi.Output[dict]
    """
    A `retry` block defining how to retry as described below.
    """
    start_time: pulumi.Output[str]
    """
    The time the first instance of the job is to start running at.
    """
    state: pulumi.Output[str]
    """
    The sets or gets the current state of the job. Can be set to either `Enabled` or `Completed`
    """
    def __init__(__self__, __name__, __opts__=None, action_storage_queue=None, action_web=None, error_action_storage_queue=None, error_action_web=None, job_collection_name=None, name=None, recurrence=None, resource_group_name=None, retry=None, start_time=None, state=None):
        """
        Manages a Scheduler Job.
        
        > **NOTE:** Support for Scheduler Job has been deprecated by Microsoft in favour of Logic Apps ([more information can be found at this link](https://docs.microsoft.com/en-us/azure/scheduler/migrate-from-scheduler-to-logic-apps)) - as such we plan to remove support for this resource as a part of version 2.0 of the AzureRM Provider.
        
        
        :param str __name__: The name of the resource.
        :param pulumi.ResourceOptions __opts__: Options for the resource.
        :param pulumi.Input[dict] action_storage_queue: A `action_storage_queue` block defining a storage queue job action as described below. Note this is identical to an `error_action_storage_queue` block.
        :param pulumi.Input[dict] action_web: A `action_web` block defining the job action as described below. Note this is identical to an `error_action_web` block.
        :param pulumi.Input[dict] error_action_storage_queue: A `error_action_storage_queue` block defining the a web action to take on an error as described below. Note this is identical to an `action_storage_queue` block.
        :param pulumi.Input[dict] error_action_web: A `error_action_web` block defining the action to take on an error as described below. Note this is identical to an `action_web` block.
        :param pulumi.Input[str] job_collection_name: Specifies the name of the Scheduler Job Collection in which the Job should exist. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: The name of the Scheduler Job. Changing this forces a new resource to be created.
        :param pulumi.Input[dict] recurrence: A `recurrence` block defining a job occurrence schedule.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the Scheduler Job. Changing this forces a new resource to be created.
        :param pulumi.Input[dict] retry: A `retry` block defining how to retry as described below.
        :param pulumi.Input[str] start_time: The time the first instance of the job is to start running at.
        :param pulumi.Input[str] state: The sets or gets the current state of the job. Can be set to either `Enabled` or `Completed`
        """
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        __props__['action_storage_queue'] = action_storage_queue

        __props__['action_web'] = action_web

        __props__['error_action_storage_queue'] = error_action_storage_queue

        __props__['error_action_web'] = error_action_web

        if not job_collection_name:
            raise TypeError('Missing required property job_collection_name')
        __props__['job_collection_name'] = job_collection_name

        __props__['name'] = name

        __props__['recurrence'] = recurrence

        if not resource_group_name:
            raise TypeError('Missing required property resource_group_name')
        __props__['resource_group_name'] = resource_group_name

        __props__['retry'] = retry

        __props__['start_time'] = start_time

        __props__['state'] = state

        super(Job, __self__).__init__(
            'azure:scheduler/job:Job',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


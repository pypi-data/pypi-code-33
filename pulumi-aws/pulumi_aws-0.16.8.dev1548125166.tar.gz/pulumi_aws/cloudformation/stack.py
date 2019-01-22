# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from .. import utilities, tables

class Stack(pulumi.CustomResource):
    capabilities: pulumi.Output[list]
    """
    A list of capabilities.
    Valid values: `CAPABILITY_IAM` or `CAPABILITY_NAMED_IAM`
    """
    disable_rollback: pulumi.Output[bool]
    """
    Set to true to disable rollback of the stack if stack creation failed.
    Conflicts with `on_failure`.
    """
    iam_role_arn: pulumi.Output[str]
    """
    The ARN of an IAM role that AWS CloudFormation assumes to create the stack. If you don't specify a value, AWS CloudFormation uses the role that was previously associated with the stack. If no role is available, AWS CloudFormation uses a temporary session that is generated from your user credentials.
    """
    name: pulumi.Output[str]
    """
    Stack name.
    """
    notification_arns: pulumi.Output[list]
    """
    A list of SNS topic ARNs to publish stack related events.
    """
    on_failure: pulumi.Output[str]
    """
    Action to be taken if stack creation fails. This must be
    one of: `DO_NOTHING`, `ROLLBACK`, or `DELETE`. Conflicts with `disable_rollback`.
    """
    outputs: pulumi.Output[dict]
    """
    A map of outputs from the stack.
    """
    parameters: pulumi.Output[dict]
    """
    A map of Parameter structures that specify input parameters for the stack.
    """
    policy_body: pulumi.Output[str]
    """
    Structure containing the stack policy body.
    Conflicts w/ `policy_url`.
    """
    policy_url: pulumi.Output[str]
    """
    Location of a file containing the stack policy.
    Conflicts w/ `policy_body`.
    """
    tags: pulumi.Output[dict]
    """
    A list of tags to associate with this stack.
    """
    template_body: pulumi.Output[str]
    """
    Structure containing the template body (max size: 51,200 bytes).
    """
    template_url: pulumi.Output[str]
    """
    Location of a file containing the template body (max size: 460,800 bytes).
    """
    timeout_in_minutes: pulumi.Output[int]
    """
    The amount of time that can pass before the stack status becomes `CREATE_FAILED`.
    """
    def __init__(__self__, __name__, __opts__=None, capabilities=None, disable_rollback=None, iam_role_arn=None, name=None, notification_arns=None, on_failure=None, parameters=None, policy_body=None, policy_url=None, tags=None, template_body=None, template_url=None, timeout_in_minutes=None):
        """
        Provides a CloudFormation Stack resource.
        
        
        :param str __name__: The name of the resource.
        :param pulumi.ResourceOptions __opts__: Options for the resource.
        :param pulumi.Input[list] capabilities: A list of capabilities.
               Valid values: `CAPABILITY_IAM` or `CAPABILITY_NAMED_IAM`
        :param pulumi.Input[bool] disable_rollback: Set to true to disable rollback of the stack if stack creation failed.
               Conflicts with `on_failure`.
        :param pulumi.Input[str] iam_role_arn: The ARN of an IAM role that AWS CloudFormation assumes to create the stack. If you don't specify a value, AWS CloudFormation uses the role that was previously associated with the stack. If no role is available, AWS CloudFormation uses a temporary session that is generated from your user credentials.
        :param pulumi.Input[str] name: Stack name.
        :param pulumi.Input[list] notification_arns: A list of SNS topic ARNs to publish stack related events.
        :param pulumi.Input[str] on_failure: Action to be taken if stack creation fails. This must be
               one of: `DO_NOTHING`, `ROLLBACK`, or `DELETE`. Conflicts with `disable_rollback`.
        :param pulumi.Input[dict] parameters: A map of Parameter structures that specify input parameters for the stack.
        :param pulumi.Input[str] policy_body: Structure containing the stack policy body.
               Conflicts w/ `policy_url`.
        :param pulumi.Input[str] policy_url: Location of a file containing the stack policy.
               Conflicts w/ `policy_body`.
        :param pulumi.Input[dict] tags: A list of tags to associate with this stack.
        :param pulumi.Input[str] template_body: Structure containing the template body (max size: 51,200 bytes).
        :param pulumi.Input[str] template_url: Location of a file containing the template body (max size: 460,800 bytes).
        :param pulumi.Input[int] timeout_in_minutes: The amount of time that can pass before the stack status becomes `CREATE_FAILED`.
        """
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        __props__['capabilities'] = capabilities

        __props__['disable_rollback'] = disable_rollback

        __props__['iam_role_arn'] = iam_role_arn

        __props__['name'] = name

        __props__['notification_arns'] = notification_arns

        __props__['on_failure'] = on_failure

        __props__['parameters'] = parameters

        __props__['policy_body'] = policy_body

        __props__['policy_url'] = policy_url

        __props__['tags'] = tags

        __props__['template_body'] = template_body

        __props__['template_url'] = template_url

        __props__['timeout_in_minutes'] = timeout_in_minutes

        __props__['outputs'] = None

        super(Stack, __self__).__init__(
            'aws:cloudformation/stack:Stack',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


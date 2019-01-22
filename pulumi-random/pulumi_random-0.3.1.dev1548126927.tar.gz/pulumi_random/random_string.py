# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import pulumi
import pulumi.runtime
from . import utilities, tables

class RandomString(pulumi.CustomResource):
    keepers: pulumi.Output[dict]
    """
    Arbitrary map of values that, when changed, will
    trigger a new id to be generated. See
    the main provider documentation for more information.
    """
    length: pulumi.Output[int]
    """
    The length of the string desired
    """
    lower: pulumi.Output[bool]
    """
    (default true) Include lowercase alphabet characters
    in random string.
    """
    min_lower: pulumi.Output[int]
    """
    (default 0) Minimum number of lowercase alphabet
    characters in random string.
    """
    min_numeric: pulumi.Output[int]
    """
    (default 0) Minimum number of numeric characters
    in random string.
    """
    min_special: pulumi.Output[int]
    """
    (default 0) Minimum number of special characters
    in random string.
    """
    min_upper: pulumi.Output[int]
    """
    (default 0) Minimum number of uppercase alphabet
    characters in random string.
    """
    number: pulumi.Output[bool]
    """
    (default true) Include numeric characters in random
    string.
    """
    override_special: pulumi.Output[str]
    """
    Supply your own list of special characters to
    use for string generation.  This overrides characters list in the special
    argument.  The special argument must still be set to true for any overwritten
    characters to be used in generation.
    """
    result: pulumi.Output[str]
    """
    Random string generated.
    """
    special: pulumi.Output[bool]
    """
    (default true) Include special characters in random
    string. These are '!@#$%&*()-_=+[]{}<>:?'
    """
    upper: pulumi.Output[bool]
    """
    (default true) Include uppercase alphabet characters
    in random string.
    """
    def __init__(__self__, __name__, __opts__=None, keepers=None, length=None, lower=None, min_lower=None, min_numeric=None, min_special=None, min_upper=None, number=None, override_special=None, special=None, upper=None):
        """
        The resource `random_string` generates a random permutation of alphanumeric
        characters and optionally special characters.
        
        This resource *does* use a cryptographic random number generator.
        
        
        :param str __name__: The name of the resource.
        :param pulumi.ResourceOptions __opts__: Options for the resource.
        :param pulumi.Input[dict] keepers: Arbitrary map of values that, when changed, will
               trigger a new id to be generated. See
               the main provider documentation for more information.
        :param pulumi.Input[int] length: The length of the string desired
        :param pulumi.Input[bool] lower: (default true) Include lowercase alphabet characters
               in random string.
        :param pulumi.Input[int] min_lower: (default 0) Minimum number of lowercase alphabet
               characters in random string.
        :param pulumi.Input[int] min_numeric: (default 0) Minimum number of numeric characters
               in random string.
        :param pulumi.Input[int] min_special: (default 0) Minimum number of special characters
               in random string.
        :param pulumi.Input[int] min_upper: (default 0) Minimum number of uppercase alphabet
               characters in random string.
        :param pulumi.Input[bool] number: (default true) Include numeric characters in random
               string.
        :param pulumi.Input[str] override_special: Supply your own list of special characters to
               use for string generation.  This overrides characters list in the special
               argument.  The special argument must still be set to true for any overwritten
               characters to be used in generation.
        :param pulumi.Input[bool] special: (default true) Include special characters in random
               string. These are '!@#$%&*()-_=+[]{}<>:?'
        :param pulumi.Input[bool] upper: (default true) Include uppercase alphabet characters
               in random string.
        """
        if not __name__:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(__name__, str):
            raise TypeError('Expected resource name to be a string')
        if __opts__ and not isinstance(__opts__, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        __props__['keepers'] = keepers

        if not length:
            raise TypeError('Missing required property length')
        __props__['length'] = length

        __props__['lower'] = lower

        __props__['min_lower'] = min_lower

        __props__['min_numeric'] = min_numeric

        __props__['min_special'] = min_special

        __props__['min_upper'] = min_upper

        __props__['number'] = number

        __props__['override_special'] = override_special

        __props__['special'] = special

        __props__['upper'] = upper

        __props__['result'] = None

        super(RandomString, __self__).__init__(
            'random:index/randomString:RandomString',
            __name__,
            __props__,
            __opts__)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop


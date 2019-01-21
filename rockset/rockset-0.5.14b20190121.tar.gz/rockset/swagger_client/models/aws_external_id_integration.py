# coding: utf-8

"""
    REST API

    Rockset's REST API allows for creating and managing all resources in Rockset. Each supported endpoint is documented below.  All requests must be authorized with a Rockset API key, which can be created in the [Rockset console](https://console.rockset.com). The API key must be provided as `ApiKey <api_key>` in the `Authorization` request header. For example: ``` Authorization: ApiKey aB35kDjg93J5nsf4GjwMeErAVd832F7ad4vhsW1S02kfZiab42sTsfW5Sxt25asT ```  All endpoints are only accessible via https.  Build something awesome!  # noqa: E501

    OpenAPI spec version: v1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class AwsExternalIdIntegration(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'aws_role_arn': 'str',
        'aws_external_id': 'str',
        'rockset_iam_user': 'str'
    }

    attribute_map = {
        'aws_role_arn': 'aws_role_arn',
        'aws_external_id': 'aws_external_id',
        'rockset_iam_user': 'rockset_iam_user'
    }

    def __init__(self, aws_role_arn, **kwargs):  # noqa: E501
        """AwsExternalIdIntegration - a model defined in Swagger"""  # noqa: E501

        self._aws_role_arn = None
        self._aws_external_id = None
        self._rockset_iam_user = None
        self.discriminator = None

        self.aws_role_arn = aws_role_arn
        self.aws_external_id = kwargs.pop('aws_external_id', None)
        self.rockset_iam_user = kwargs.pop('rockset_iam_user', None)

    @property
    def aws_role_arn(self):
        """Gets the aws_role_arn of this AwsExternalIdIntegration.  # noqa: E501

        ARN of rockset-role created in your account  # noqa: E501

        :return: The aws_role_arn of this AwsExternalIdIntegration.  # noqa: E501
        :rtype: str
        """
        return self._aws_role_arn

    @aws_role_arn.setter
    def aws_role_arn(self, aws_role_arn):
        """Sets the aws_role_arn of this AwsExternalIdIntegration.

        ARN of rockset-role created in your account  # noqa: E501

        :param aws_role_arn: The aws_role_arn of this AwsExternalIdIntegration.  # noqa: E501
        :type: str
        """

        self._aws_role_arn = aws_role_arn

    @property
    def aws_external_id(self):
        """Gets the aws_external_id of this AwsExternalIdIntegration.  # noqa: E501


        :return: The aws_external_id of this AwsExternalIdIntegration.  # noqa: E501
        :rtype: str
        """
        return self._aws_external_id

    @aws_external_id.setter
    def aws_external_id(self, aws_external_id):
        """Sets the aws_external_id of this AwsExternalIdIntegration.


        :param aws_external_id: The aws_external_id of this AwsExternalIdIntegration.  # noqa: E501
        :type: str
        """

        self._aws_external_id = aws_external_id

    @property
    def rockset_iam_user(self):
        """Gets the rockset_iam_user of this AwsExternalIdIntegration.  # noqa: E501


        :return: The rockset_iam_user of this AwsExternalIdIntegration.  # noqa: E501
        :rtype: str
        """
        return self._rockset_iam_user

    @rockset_iam_user.setter
    def rockset_iam_user(self, rockset_iam_user):
        """Sets the rockset_iam_user of this AwsExternalIdIntegration.


        :param rockset_iam_user: The rockset_iam_user of this AwsExternalIdIntegration.  # noqa: E501
        :type: str
        """

        self._rockset_iam_user = rockset_iam_user

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(AwsExternalIdIntegration, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, AwsExternalIdIntegration):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

    def __getitem__(self, item):
        return getattr(self, item)

    def get(self, item):
        return getattr(self, item)

    def items(self):
        return self.to_dict().items()

    def __setitem__(self, item, value):
        return seattr(self, item, value)

# coding: utf-8

"""
    CallER API

    CallER API in the cloud service  # noqa: E501

    OpenAPI spec version: 3.3.0
    Contact: api@behavioralsignals.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class ResultJSONCoreValue(object):
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
        'agent': 'float',
        'customer': 'float'
    }

    attribute_map = {
        'agent': 'agent',
        'customer': 'customer'
    }

    def __init__(self, agent=None, customer=None):  # noqa: E501
        """ResultJSONCoreValue - a model defined in Swagger"""  # noqa: E501

        self._agent = None
        self._customer = None
        self.discriminator = None

        if agent is not None:
            self.agent = agent
        if customer is not None:
            self.customer = customer

    @property
    def agent(self):
        """Gets the agent of this ResultJSONCoreValue.  # noqa: E501

        Aggregated value in the 0, 1 range  # noqa: E501

        :return: The agent of this ResultJSONCoreValue.  # noqa: E501
        :rtype: float
        """
        return self._agent

    @agent.setter
    def agent(self, agent):
        """Sets the agent of this ResultJSONCoreValue.

        Aggregated value in the 0, 1 range  # noqa: E501

        :param agent: The agent of this ResultJSONCoreValue.  # noqa: E501
        :type: float
        """

        self._agent = agent

    @property
    def customer(self):
        """Gets the customer of this ResultJSONCoreValue.  # noqa: E501

        Aggregated value in the 0, 1 range  # noqa: E501

        :return: The customer of this ResultJSONCoreValue.  # noqa: E501
        :rtype: float
        """
        return self._customer

    @customer.setter
    def customer(self, customer):
        """Sets the customer of this ResultJSONCoreValue.

        Aggregated value in the 0, 1 range  # noqa: E501

        :param customer: The customer of this ResultJSONCoreValue.  # noqa: E501
        :type: float
        """

        self._customer = customer

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
        if issubclass(ResultJSONCoreValue, dict):
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
        if not isinstance(other, ResultJSONCoreValue):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

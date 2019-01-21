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

from behavioral_signals_swagger_client.models.result_json_core_emotions_anger import ResultJSONCoreEmotionsAnger  # noqa: F401,E501
from behavioral_signals_swagger_client.models.result_json_core_emotions_frustration import ResultJSONCoreEmotionsFrustration  # noqa: F401,E501
from behavioral_signals_swagger_client.models.result_json_core_emotions_happy import ResultJSONCoreEmotionsHappy  # noqa: F401,E501
from behavioral_signals_swagger_client.models.result_json_core_emotions_sad import ResultJSONCoreEmotionsSad  # noqa: F401,E501


class ResultJSONCoreEmotions(object):
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
        'happy': 'ResultJSONCoreEmotionsHappy',
        'anger': 'ResultJSONCoreEmotionsAnger',
        'frustration': 'ResultJSONCoreEmotionsFrustration',
        'sad': 'ResultJSONCoreEmotionsSad'
    }

    attribute_map = {
        'happy': 'happy',
        'anger': 'anger',
        'frustration': 'frustration',
        'sad': 'sad'
    }

    def __init__(self, happy=None, anger=None, frustration=None, sad=None):  # noqa: E501
        """ResultJSONCoreEmotions - a model defined in Swagger"""  # noqa: E501

        self._happy = None
        self._anger = None
        self._frustration = None
        self._sad = None
        self.discriminator = None

        if happy is not None:
            self.happy = happy
        if anger is not None:
            self.anger = anger
        if frustration is not None:
            self.frustration = frustration
        if sad is not None:
            self.sad = sad

    @property
    def happy(self):
        """Gets the happy of this ResultJSONCoreEmotions.  # noqa: E501


        :return: The happy of this ResultJSONCoreEmotions.  # noqa: E501
        :rtype: ResultJSONCoreEmotionsHappy
        """
        return self._happy

    @happy.setter
    def happy(self, happy):
        """Sets the happy of this ResultJSONCoreEmotions.


        :param happy: The happy of this ResultJSONCoreEmotions.  # noqa: E501
        :type: ResultJSONCoreEmotionsHappy
        """

        self._happy = happy

    @property
    def anger(self):
        """Gets the anger of this ResultJSONCoreEmotions.  # noqa: E501


        :return: The anger of this ResultJSONCoreEmotions.  # noqa: E501
        :rtype: ResultJSONCoreEmotionsAnger
        """
        return self._anger

    @anger.setter
    def anger(self, anger):
        """Sets the anger of this ResultJSONCoreEmotions.


        :param anger: The anger of this ResultJSONCoreEmotions.  # noqa: E501
        :type: ResultJSONCoreEmotionsAnger
        """

        self._anger = anger

    @property
    def frustration(self):
        """Gets the frustration of this ResultJSONCoreEmotions.  # noqa: E501


        :return: The frustration of this ResultJSONCoreEmotions.  # noqa: E501
        :rtype: ResultJSONCoreEmotionsFrustration
        """
        return self._frustration

    @frustration.setter
    def frustration(self, frustration):
        """Sets the frustration of this ResultJSONCoreEmotions.


        :param frustration: The frustration of this ResultJSONCoreEmotions.  # noqa: E501
        :type: ResultJSONCoreEmotionsFrustration
        """

        self._frustration = frustration

    @property
    def sad(self):
        """Gets the sad of this ResultJSONCoreEmotions.  # noqa: E501


        :return: The sad of this ResultJSONCoreEmotions.  # noqa: E501
        :rtype: ResultJSONCoreEmotionsSad
        """
        return self._sad

    @sad.setter
    def sad(self, sad):
        """Sets the sad of this ResultJSONCoreEmotions.


        :param sad: The sad of this ResultJSONCoreEmotions.  # noqa: E501
        :type: ResultJSONCoreEmotionsSad
        """

        self._sad = sad

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
        if issubclass(ResultJSONCoreEmotions, dict):
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
        if not isinstance(other, ResultJSONCoreEmotions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

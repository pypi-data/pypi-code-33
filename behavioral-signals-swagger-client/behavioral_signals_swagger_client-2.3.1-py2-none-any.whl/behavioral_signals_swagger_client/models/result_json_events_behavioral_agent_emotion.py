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


class ResultJSONEventsBehavioralAgentEmotion(object):
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
        'st': 'float',
        'et': 'float',
        'label': 'str',
        'confidence': 'float'
    }

    attribute_map = {
        'st': 'st',
        'et': 'et',
        'label': 'label',
        'confidence': 'confidence'
    }

    def __init__(self, st=None, et=None, label=None, confidence=None):  # noqa: E501
        """ResultJSONEventsBehavioralAgentEmotion - a model defined in Swagger"""  # noqa: E501

        self._st = None
        self._et = None
        self._label = None
        self._confidence = None
        self.discriminator = None

        if st is not None:
            self.st = st
        if et is not None:
            self.et = et
        if label is not None:
            self.label = label
        if confidence is not None:
            self.confidence = confidence

    @property
    def st(self):
        """Gets the st of this ResultJSONEventsBehavioralAgentEmotion.  # noqa: E501

        start time in seconds  # noqa: E501

        :return: The st of this ResultJSONEventsBehavioralAgentEmotion.  # noqa: E501
        :rtype: float
        """
        return self._st

    @st.setter
    def st(self, st):
        """Sets the st of this ResultJSONEventsBehavioralAgentEmotion.

        start time in seconds  # noqa: E501

        :param st: The st of this ResultJSONEventsBehavioralAgentEmotion.  # noqa: E501
        :type: float
        """

        self._st = st

    @property
    def et(self):
        """Gets the et of this ResultJSONEventsBehavioralAgentEmotion.  # noqa: E501

        end time in seconds  # noqa: E501

        :return: The et of this ResultJSONEventsBehavioralAgentEmotion.  # noqa: E501
        :rtype: float
        """
        return self._et

    @et.setter
    def et(self, et):
        """Sets the et of this ResultJSONEventsBehavioralAgentEmotion.

        end time in seconds  # noqa: E501

        :param et: The et of this ResultJSONEventsBehavioralAgentEmotion.  # noqa: E501
        :type: float
        """

        self._et = et

    @property
    def label(self):
        """Gets the label of this ResultJSONEventsBehavioralAgentEmotion.  # noqa: E501

        event label: happy/angry/sad/frustrated  # noqa: E501

        :return: The label of this ResultJSONEventsBehavioralAgentEmotion.  # noqa: E501
        :rtype: str
        """
        return self._label

    @label.setter
    def label(self, label):
        """Sets the label of this ResultJSONEventsBehavioralAgentEmotion.

        event label: happy/angry/sad/frustrated  # noqa: E501

        :param label: The label of this ResultJSONEventsBehavioralAgentEmotion.  # noqa: E501
        :type: str
        """

        self._label = label

    @property
    def confidence(self):
        """Gets the confidence of this ResultJSONEventsBehavioralAgentEmotion.  # noqa: E501

        confidence score, between 0 and 1  # noqa: E501

        :return: The confidence of this ResultJSONEventsBehavioralAgentEmotion.  # noqa: E501
        :rtype: float
        """
        return self._confidence

    @confidence.setter
    def confidence(self, confidence):
        """Sets the confidence of this ResultJSONEventsBehavioralAgentEmotion.

        confidence score, between 0 and 1  # noqa: E501

        :param confidence: The confidence of this ResultJSONEventsBehavioralAgentEmotion.  # noqa: E501
        :type: float
        """

        self._confidence = confidence

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
        if issubclass(ResultJSONEventsBehavioralAgentEmotion, dict):
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
        if not isinstance(other, ResultJSONEventsBehavioralAgentEmotion):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

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

from behavioral_signals_swagger_client.models.result_json_frames_frames import ResultJSONFramesFrames  # noqa: F401,E501


class ResultJSONFrames(object):
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
        'frames': 'list[ResultJSONFramesFrames]'
    }

    attribute_map = {
        'frames': 'frames'
    }

    def __init__(self, frames=None):  # noqa: E501
        """ResultJSONFrames - a model defined in Swagger"""  # noqa: E501

        self._frames = None
        self.discriminator = None

        self.frames = frames

    @property
    def frames(self):
        """Gets the frames of this ResultJSONFrames.  # noqa: E501

        Contains frame results  # noqa: E501

        :return: The frames of this ResultJSONFrames.  # noqa: E501
        :rtype: list[ResultJSONFramesFrames]
        """
        return self._frames

    @frames.setter
    def frames(self, frames):
        """Sets the frames of this ResultJSONFrames.

        Contains frame results  # noqa: E501

        :param frames: The frames of this ResultJSONFrames.  # noqa: E501
        :type: list[ResultJSONFramesFrames]
        """
        if frames is None:
            raise ValueError("Invalid value for `frames`, must not be `None`")  # noqa: E501

        self._frames = frames

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
        if issubclass(ResultJSONFrames, dict):
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
        if not isinstance(other, ResultJSONFrames):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

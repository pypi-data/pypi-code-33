# coding: utf-8

"""
    Endpoints

    Endpoints API for different services in SKIL  # noqa: E501

    OpenAPI spec version: 1.2.0-rc1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class AggregatePrediction(object):
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
        'model_id': 'str',
        'eval_type': 'str'
    }

    attribute_map = {
        'model_id': 'modelId',
        'eval_type': 'evalType'
    }

    def __init__(self, model_id=None, eval_type=None):  # noqa: E501
        """AggregatePrediction - a model defined in Swagger"""  # noqa: E501

        self._model_id = None
        self._eval_type = None
        self.discriminator = None

        if model_id is not None:
            self.model_id = model_id
        if eval_type is not None:
            self.eval_type = eval_type

    @property
    def model_id(self):
        """Gets the model_id of this AggregatePrediction.  # noqa: E501

        GUID of model instance  # noqa: E501

        :return: The model_id of this AggregatePrediction.  # noqa: E501
        :rtype: str
        """
        return self._model_id

    @model_id.setter
    def model_id(self, model_id):
        """Sets the model_id of this AggregatePrediction.

        GUID of model instance  # noqa: E501

        :param model_id: The model_id of this AggregatePrediction.  # noqa: E501
        :type: str
        """

        self._model_id = model_id

    @property
    def eval_type(self):
        """Gets the eval_type of this AggregatePrediction.  # noqa: E501

        the evaluation type to aggregate  # noqa: E501

        :return: The eval_type of this AggregatePrediction.  # noqa: E501
        :rtype: str
        """
        return self._eval_type

    @eval_type.setter
    def eval_type(self, eval_type):
        """Sets the eval_type of this AggregatePrediction.

        the evaluation type to aggregate  # noqa: E501

        :param eval_type: The eval_type of this AggregatePrediction.  # noqa: E501
        :type: str
        """
        allowed_values = ["ROC_BINARY", "ROC", "EVALUATION_BINARY", "EVALUATION", "REGRESSON_EVALUATION", "ROC_MULTI_CLASS"]  # noqa: E501
        if eval_type not in allowed_values:
            raise ValueError(
                "Invalid value for `eval_type` ({0}), must be one of {1}"  # noqa: E501
                .format(eval_type, allowed_values)
            )

        self._eval_type = eval_type

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

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, AggregatePrediction):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

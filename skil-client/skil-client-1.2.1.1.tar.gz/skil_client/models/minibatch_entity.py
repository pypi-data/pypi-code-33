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


class MinibatchEntity(object):
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
        'mini_batch_id': 'str',
        'eval_id': 'str',
        'eval_version': 'int',
        'batch_version': 'int'
    }

    attribute_map = {
        'mini_batch_id': 'miniBatchId',
        'eval_id': 'evalId',
        'eval_version': 'evalVersion',
        'batch_version': 'batchVersion'
    }

    def __init__(self, mini_batch_id=None, eval_id=None, eval_version=None, batch_version=None):  # noqa: E501
        """MinibatchEntity - a model defined in Swagger"""  # noqa: E501

        self._mini_batch_id = None
        self._eval_id = None
        self._eval_version = None
        self._batch_version = None
        self.discriminator = None

        if mini_batch_id is not None:
            self.mini_batch_id = mini_batch_id
        if eval_id is not None:
            self.eval_id = eval_id
        if eval_version is not None:
            self.eval_version = eval_version
        if batch_version is not None:
            self.batch_version = batch_version

    @property
    def mini_batch_id(self):
        """Gets the mini_batch_id of this MinibatchEntity.  # noqa: E501

        GUID of mini batch  # noqa: E501

        :return: The mini_batch_id of this MinibatchEntity.  # noqa: E501
        :rtype: str
        """
        return self._mini_batch_id

    @mini_batch_id.setter
    def mini_batch_id(self, mini_batch_id):
        """Sets the mini_batch_id of this MinibatchEntity.

        GUID of mini batch  # noqa: E501

        :param mini_batch_id: The mini_batch_id of this MinibatchEntity.  # noqa: E501
        :type: str
        """

        self._mini_batch_id = mini_batch_id

    @property
    def eval_id(self):
        """Gets the eval_id of this MinibatchEntity.  # noqa: E501

        GUID of the evaluation  # noqa: E501

        :return: The eval_id of this MinibatchEntity.  # noqa: E501
        :rtype: str
        """
        return self._eval_id

    @eval_id.setter
    def eval_id(self, eval_id):
        """Sets the eval_id of this MinibatchEntity.

        GUID of the evaluation  # noqa: E501

        :param eval_id: The eval_id of this MinibatchEntity.  # noqa: E501
        :type: str
        """

        self._eval_id = eval_id

    @property
    def eval_version(self):
        """Gets the eval_version of this MinibatchEntity.  # noqa: E501

        Eval version  # noqa: E501

        :return: The eval_version of this MinibatchEntity.  # noqa: E501
        :rtype: int
        """
        return self._eval_version

    @eval_version.setter
    def eval_version(self, eval_version):
        """Sets the eval_version of this MinibatchEntity.

        Eval version  # noqa: E501

        :param eval_version: The eval_version of this MinibatchEntity.  # noqa: E501
        :type: int
        """

        self._eval_version = eval_version

    @property
    def batch_version(self):
        """Gets the batch_version of this MinibatchEntity.  # noqa: E501

        Batch version  # noqa: E501

        :return: The batch_version of this MinibatchEntity.  # noqa: E501
        :rtype: int
        """
        return self._batch_version

    @batch_version.setter
    def batch_version(self, batch_version):
        """Sets the batch_version of this MinibatchEntity.

        Batch version  # noqa: E501

        :param batch_version: The batch_version of this MinibatchEntity.  # noqa: E501
        :type: int
        """

        self._batch_version = batch_version

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
        if not isinstance(other, MinibatchEntity):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

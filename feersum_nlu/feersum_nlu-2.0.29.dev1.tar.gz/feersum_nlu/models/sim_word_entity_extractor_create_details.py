# coding: utf-8

"""
    FeersumNLU API

    This is the HTTP API for Feersum NLU. See https://github.com/praekelt/feersum-nlu-api-wrappers for examples of how to use the API.  # noqa: E501

    OpenAPI spec version: 2.0.28
    Contact: nlu@feersum.io
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class SimWordEntityExtractorCreateDetails(object):
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
        'name': 'str',
        'long_name': 'str',
        'desc': 'str',
        'similar_words': 'list[str]',
        'threshold': 'float',
        'word_manifold': 'str',
        'load_from_store': 'bool'
    }

    attribute_map = {
        'name': 'name',
        'long_name': 'long_name',
        'desc': 'desc',
        'similar_words': 'similar_words',
        'threshold': 'threshold',
        'word_manifold': 'word_manifold',
        'load_from_store': 'load_from_store'
    }

    def __init__(self, name=None, long_name=None, desc=None, similar_words=None, threshold=None, word_manifold=None, load_from_store=None):  # noqa: E501
        """SimWordEntityExtractorCreateDetails - a model defined in Swagger"""  # noqa: E501

        self._name = None
        self._long_name = None
        self._desc = None
        self._similar_words = None
        self._threshold = None
        self._word_manifold = None
        self._load_from_store = None
        self.discriminator = None

        self.name = name
        if long_name is not None:
            self.long_name = long_name
        if desc is not None:
            self.desc = desc
        if similar_words is not None:
            self.similar_words = similar_words
        if threshold is not None:
            self.threshold = threshold
        if word_manifold is not None:
            self.word_manifold = word_manifold
        self.load_from_store = load_from_store

    @property
    def name(self):
        """Gets the name of this SimWordEntityExtractorCreateDetails.  # noqa: E501

        The sluggy-url-friendly-name of the instance to create.  # noqa: E501

        :return: The name of this SimWordEntityExtractorCreateDetails.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this SimWordEntityExtractorCreateDetails.

        The sluggy-url-friendly-name of the instance to create.  # noqa: E501

        :param name: The name of this SimWordEntityExtractorCreateDetails.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def long_name(self):
        """Gets the long_name of this SimWordEntityExtractorCreateDetails.  # noqa: E501

        The human-friendly-name of the instance.  # noqa: E501

        :return: The long_name of this SimWordEntityExtractorCreateDetails.  # noqa: E501
        :rtype: str
        """
        return self._long_name

    @long_name.setter
    def long_name(self, long_name):
        """Sets the long_name of this SimWordEntityExtractorCreateDetails.

        The human-friendly-name of the instance.  # noqa: E501

        :param long_name: The long_name of this SimWordEntityExtractorCreateDetails.  # noqa: E501
        :type: str
        """

        self._long_name = long_name

    @property
    def desc(self):
        """Gets the desc of this SimWordEntityExtractorCreateDetails.  # noqa: E501

        The longer existential description of this instance's purpose in life.  # noqa: E501

        :return: The desc of this SimWordEntityExtractorCreateDetails.  # noqa: E501
        :rtype: str
        """
        return self._desc

    @desc.setter
    def desc(self, desc):
        """Sets the desc of this SimWordEntityExtractorCreateDetails.

        The longer existential description of this instance's purpose in life.  # noqa: E501

        :param desc: The desc of this SimWordEntityExtractorCreateDetails.  # noqa: E501
        :type: str
        """

        self._desc = desc

    @property
    def similar_words(self):
        """Gets the similar_words of this SimWordEntityExtractorCreateDetails.  # noqa: E501


        :return: The similar_words of this SimWordEntityExtractorCreateDetails.  # noqa: E501
        :rtype: list[str]
        """
        return self._similar_words

    @similar_words.setter
    def similar_words(self, similar_words):
        """Sets the similar_words of this SimWordEntityExtractorCreateDetails.


        :param similar_words: The similar_words of this SimWordEntityExtractorCreateDetails.  # noqa: E501
        :type: list[str]
        """

        self._similar_words = similar_words

    @property
    def threshold(self):
        """Gets the threshold of this SimWordEntityExtractorCreateDetails.  # noqa: E501

        The threshold below which words are not similar.  # noqa: E501

        :return: The threshold of this SimWordEntityExtractorCreateDetails.  # noqa: E501
        :rtype: float
        """
        return self._threshold

    @threshold.setter
    def threshold(self, threshold):
        """Sets the threshold of this SimWordEntityExtractorCreateDetails.

        The threshold below which words are not similar.  # noqa: E501

        :param threshold: The threshold of this SimWordEntityExtractorCreateDetails.  # noqa: E501
        :type: float
        """

        self._threshold = threshold

    @property
    def word_manifold(self):
        """Gets the word_manifold of this SimWordEntityExtractorCreateDetails.  # noqa: E501


        :return: The word_manifold of this SimWordEntityExtractorCreateDetails.  # noqa: E501
        :rtype: str
        """
        return self._word_manifold

    @word_manifold.setter
    def word_manifold(self, word_manifold):
        """Sets the word_manifold of this SimWordEntityExtractorCreateDetails.


        :param word_manifold: The word_manifold of this SimWordEntityExtractorCreateDetails.  # noqa: E501
        :type: str
        """

        self._word_manifold = word_manifold

    @property
    def load_from_store(self):
        """Gets the load_from_store of this SimWordEntityExtractorCreateDetails.  # noqa: E501

        Indicates if a pre-existing model with the specified name should be loaded from the trash. Usually set to False in which case a new model is created with details as specified.  # noqa: E501

        :return: The load_from_store of this SimWordEntityExtractorCreateDetails.  # noqa: E501
        :rtype: bool
        """
        return self._load_from_store

    @load_from_store.setter
    def load_from_store(self, load_from_store):
        """Sets the load_from_store of this SimWordEntityExtractorCreateDetails.

        Indicates if a pre-existing model with the specified name should be loaded from the trash. Usually set to False in which case a new model is created with details as specified.  # noqa: E501

        :param load_from_store: The load_from_store of this SimWordEntityExtractorCreateDetails.  # noqa: E501
        :type: bool
        """
        if load_from_store is None:
            raise ValueError("Invalid value for `load_from_store`, must not be `None`")  # noqa: E501

        self._load_from_store = load_from_store

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
        if not isinstance(other, SimWordEntityExtractorCreateDetails):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

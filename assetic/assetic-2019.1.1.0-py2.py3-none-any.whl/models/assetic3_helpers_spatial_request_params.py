# coding: utf-8

"""
    Assetic Integration API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: v2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class Assetic3HelpersSpatialRequestParams(object):
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
        'longitude': 'float',
        'latitude': 'float',
        'condition': 'str',
        'range': 'float',
        'unit': 'str',
        'page': 'int',
        'page_size': 'int'
    }

    attribute_map = {
        'longitude': 'Longitude',
        'latitude': 'Latitude',
        'condition': 'Condition',
        'range': 'Range',
        'unit': 'Unit',
        'page': 'Page',
        'page_size': 'PageSize'
    }

    def __init__(self, longitude=None, latitude=None, condition=None, range=None, unit=None, page=None, page_size=None):  # noqa: E501
        """Assetic3HelpersSpatialRequestParams - a model defined in Swagger"""  # noqa: E501

        self._longitude = None
        self._latitude = None
        self._condition = None
        self._range = None
        self._unit = None
        self._page = None
        self._page_size = None
        self.discriminator = None

        if longitude is not None:
            self.longitude = longitude
        if latitude is not None:
            self.latitude = latitude
        if condition is not None:
            self.condition = condition
        if range is not None:
            self.range = range
        if unit is not None:
            self.unit = unit
        if page is not None:
            self.page = page
        if page_size is not None:
            self.page_size = page_size

    @property
    def longitude(self):
        """Gets the longitude of this Assetic3HelpersSpatialRequestParams.  # noqa: E501


        :return: The longitude of this Assetic3HelpersSpatialRequestParams.  # noqa: E501
        :rtype: float
        """
        return self._longitude

    @longitude.setter
    def longitude(self, longitude):
        """Sets the longitude of this Assetic3HelpersSpatialRequestParams.


        :param longitude: The longitude of this Assetic3HelpersSpatialRequestParams.  # noqa: E501
        :type: float
        """

        self._longitude = longitude

    @property
    def latitude(self):
        """Gets the latitude of this Assetic3HelpersSpatialRequestParams.  # noqa: E501


        :return: The latitude of this Assetic3HelpersSpatialRequestParams.  # noqa: E501
        :rtype: float
        """
        return self._latitude

    @latitude.setter
    def latitude(self, latitude):
        """Sets the latitude of this Assetic3HelpersSpatialRequestParams.


        :param latitude: The latitude of this Assetic3HelpersSpatialRequestParams.  # noqa: E501
        :type: float
        """

        self._latitude = latitude

    @property
    def condition(self):
        """Gets the condition of this Assetic3HelpersSpatialRequestParams.  # noqa: E501


        :return: The condition of this Assetic3HelpersSpatialRequestParams.  # noqa: E501
        :rtype: str
        """
        return self._condition

    @condition.setter
    def condition(self, condition):
        """Sets the condition of this Assetic3HelpersSpatialRequestParams.


        :param condition: The condition of this Assetic3HelpersSpatialRequestParams.  # noqa: E501
        :type: str
        """

        self._condition = condition

    @property
    def range(self):
        """Gets the range of this Assetic3HelpersSpatialRequestParams.  # noqa: E501


        :return: The range of this Assetic3HelpersSpatialRequestParams.  # noqa: E501
        :rtype: float
        """
        return self._range

    @range.setter
    def range(self, range):
        """Sets the range of this Assetic3HelpersSpatialRequestParams.


        :param range: The range of this Assetic3HelpersSpatialRequestParams.  # noqa: E501
        :type: float
        """

        self._range = range

    @property
    def unit(self):
        """Gets the unit of this Assetic3HelpersSpatialRequestParams.  # noqa: E501


        :return: The unit of this Assetic3HelpersSpatialRequestParams.  # noqa: E501
        :rtype: str
        """
        return self._unit

    @unit.setter
    def unit(self, unit):
        """Sets the unit of this Assetic3HelpersSpatialRequestParams.


        :param unit: The unit of this Assetic3HelpersSpatialRequestParams.  # noqa: E501
        :type: str
        """

        self._unit = unit

    @property
    def page(self):
        """Gets the page of this Assetic3HelpersSpatialRequestParams.  # noqa: E501


        :return: The page of this Assetic3HelpersSpatialRequestParams.  # noqa: E501
        :rtype: int
        """
        return self._page

    @page.setter
    def page(self, page):
        """Sets the page of this Assetic3HelpersSpatialRequestParams.


        :param page: The page of this Assetic3HelpersSpatialRequestParams.  # noqa: E501
        :type: int
        """

        self._page = page

    @property
    def page_size(self):
        """Gets the page_size of this Assetic3HelpersSpatialRequestParams.  # noqa: E501


        :return: The page_size of this Assetic3HelpersSpatialRequestParams.  # noqa: E501
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this Assetic3HelpersSpatialRequestParams.


        :param page_size: The page_size of this Assetic3HelpersSpatialRequestParams.  # noqa: E501
        :type: int
        """

        self._page_size = page_size

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
        if issubclass(Assetic3HelpersSpatialRequestParams, dict):
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
        if not isinstance(other, Assetic3HelpersSpatialRequestParams):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

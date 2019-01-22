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

##from assetic.models.web_api_hal_embedded_resource import WebApiHalEmbeddedResource  # noqa: F401,E501
##from assetic.models.web_api_hal_link import WebApiHalLink  # noqa: F401,E501


class Assetic3IntegrationRepresentationsMaintenanceScheduling(object):
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
        'due_date': 'str',
        'target_start': 'str',
        'target_finish': 'str',
        'actual_start': 'str',
        'actual_finish': 'str',
        'scheduled_start': 'str',
        'scheduled_finish': 'str',
        'links': 'list[WebApiHalLink]',
        'embedded': 'list[WebApiHalEmbeddedResource]'
    }

    attribute_map = {
        'due_date': 'DueDate',
        'target_start': 'TargetStart',
        'target_finish': 'TargetFinish',
        'actual_start': 'ActualStart',
        'actual_finish': 'ActualFinish',
        'scheduled_start': 'ScheduledStart',
        'scheduled_finish': 'ScheduledFinish',
        'links': '_links',
        'embedded': '_embedded'
    }

    def __init__(self, due_date=None, target_start=None, target_finish=None, actual_start=None, actual_finish=None, scheduled_start=None, scheduled_finish=None, links=None, embedded=None):  # noqa: E501
        """Assetic3IntegrationRepresentationsMaintenanceScheduling - a model defined in Swagger"""  # noqa: E501

        self._due_date = None
        self._target_start = None
        self._target_finish = None
        self._actual_start = None
        self._actual_finish = None
        self._scheduled_start = None
        self._scheduled_finish = None
        self._links = None
        self._embedded = None
        self.discriminator = None

        if due_date is not None:
            self.due_date = due_date
        if target_start is not None:
            self.target_start = target_start
        if target_finish is not None:
            self.target_finish = target_finish
        if actual_start is not None:
            self.actual_start = actual_start
        if actual_finish is not None:
            self.actual_finish = actual_finish
        if scheduled_start is not None:
            self.scheduled_start = scheduled_start
        if scheduled_finish is not None:
            self.scheduled_finish = scheduled_finish
        if links is not None:
            self.links = links
        if embedded is not None:
            self.embedded = embedded

    @property
    def due_date(self):
        """Gets the due_date of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501


        :return: The due_date of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :rtype: str
        """
        return self._due_date

    @due_date.setter
    def due_date(self, due_date):
        """Sets the due_date of this Assetic3IntegrationRepresentationsMaintenanceScheduling.


        :param due_date: The due_date of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :type: str
        """

        self._due_date = due_date

    @property
    def target_start(self):
        """Gets the target_start of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501


        :return: The target_start of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :rtype: str
        """
        return self._target_start

    @target_start.setter
    def target_start(self, target_start):
        """Sets the target_start of this Assetic3IntegrationRepresentationsMaintenanceScheduling.


        :param target_start: The target_start of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :type: str
        """

        self._target_start = target_start

    @property
    def target_finish(self):
        """Gets the target_finish of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501


        :return: The target_finish of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :rtype: str
        """
        return self._target_finish

    @target_finish.setter
    def target_finish(self, target_finish):
        """Sets the target_finish of this Assetic3IntegrationRepresentationsMaintenanceScheduling.


        :param target_finish: The target_finish of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :type: str
        """

        self._target_finish = target_finish

    @property
    def actual_start(self):
        """Gets the actual_start of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501


        :return: The actual_start of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :rtype: str
        """
        return self._actual_start

    @actual_start.setter
    def actual_start(self, actual_start):
        """Sets the actual_start of this Assetic3IntegrationRepresentationsMaintenanceScheduling.


        :param actual_start: The actual_start of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :type: str
        """

        self._actual_start = actual_start

    @property
    def actual_finish(self):
        """Gets the actual_finish of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501


        :return: The actual_finish of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :rtype: str
        """
        return self._actual_finish

    @actual_finish.setter
    def actual_finish(self, actual_finish):
        """Sets the actual_finish of this Assetic3IntegrationRepresentationsMaintenanceScheduling.


        :param actual_finish: The actual_finish of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :type: str
        """

        self._actual_finish = actual_finish

    @property
    def scheduled_start(self):
        """Gets the scheduled_start of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501


        :return: The scheduled_start of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :rtype: str
        """
        return self._scheduled_start

    @scheduled_start.setter
    def scheduled_start(self, scheduled_start):
        """Sets the scheduled_start of this Assetic3IntegrationRepresentationsMaintenanceScheduling.


        :param scheduled_start: The scheduled_start of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :type: str
        """

        self._scheduled_start = scheduled_start

    @property
    def scheduled_finish(self):
        """Gets the scheduled_finish of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501


        :return: The scheduled_finish of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :rtype: str
        """
        return self._scheduled_finish

    @scheduled_finish.setter
    def scheduled_finish(self, scheduled_finish):
        """Sets the scheduled_finish of this Assetic3IntegrationRepresentationsMaintenanceScheduling.


        :param scheduled_finish: The scheduled_finish of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :type: str
        """

        self._scheduled_finish = scheduled_finish

    @property
    def links(self):
        """Gets the links of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501


        :return: The links of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :rtype: list[WebApiHalLink]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this Assetic3IntegrationRepresentationsMaintenanceScheduling.


        :param links: The links of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :type: list[WebApiHalLink]
        """

        self._links = links

    @property
    def embedded(self):
        """Gets the embedded of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501


        :return: The embedded of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :rtype: list[WebApiHalEmbeddedResource]
        """
        return self._embedded

    @embedded.setter
    def embedded(self, embedded):
        """Sets the embedded of this Assetic3IntegrationRepresentationsMaintenanceScheduling.


        :param embedded: The embedded of this Assetic3IntegrationRepresentationsMaintenanceScheduling.  # noqa: E501
        :type: list[WebApiHalEmbeddedResource]
        """

        self._embedded = embedded

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
        if issubclass(Assetic3IntegrationRepresentationsMaintenanceScheduling, dict):
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
        if not isinstance(other, Assetic3IntegrationRepresentationsMaintenanceScheduling):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

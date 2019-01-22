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


class Assetic3IntegrationRepresentationsMaintenanceAsset(object):
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
        'id': 'str',
        'asset_id': 'str',
        'asset_name': 'str',
        'work_group_id': 'int',
        'asset_work_group': 'str',
        'criticality_id': 'str',
        'asset_criticality': 'str',
        'asset_category_id': 'str',
        'asset_category': 'str',
        'asset_maintenance_type': 'str',
        'links': 'list[WebApiHalLink]',
        'embedded': 'list[WebApiHalEmbeddedResource]'
    }

    attribute_map = {
        'id': 'Id',
        'asset_id': 'AssetId',
        'asset_name': 'AssetName',
        'work_group_id': 'WorkGroupId',
        'asset_work_group': 'AssetWorkGroup',
        'criticality_id': 'CriticalityId',
        'asset_criticality': 'AssetCriticality',
        'asset_category_id': 'AssetCategoryId',
        'asset_category': 'AssetCategory',
        'asset_maintenance_type': 'AssetMaintenanceType',
        'links': '_links',
        'embedded': '_embedded'
    }

    def __init__(self, id=None, asset_id=None, asset_name=None, work_group_id=None, asset_work_group=None, criticality_id=None, asset_criticality=None, asset_category_id=None, asset_category=None, asset_maintenance_type=None, links=None, embedded=None):  # noqa: E501
        """Assetic3IntegrationRepresentationsMaintenanceAsset - a model defined in Swagger"""  # noqa: E501

        self._id = None
        self._asset_id = None
        self._asset_name = None
        self._work_group_id = None
        self._asset_work_group = None
        self._criticality_id = None
        self._asset_criticality = None
        self._asset_category_id = None
        self._asset_category = None
        self._asset_maintenance_type = None
        self._links = None
        self._embedded = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if asset_id is not None:
            self.asset_id = asset_id
        if asset_name is not None:
            self.asset_name = asset_name
        if work_group_id is not None:
            self.work_group_id = work_group_id
        if asset_work_group is not None:
            self.asset_work_group = asset_work_group
        if criticality_id is not None:
            self.criticality_id = criticality_id
        if asset_criticality is not None:
            self.asset_criticality = asset_criticality
        if asset_category_id is not None:
            self.asset_category_id = asset_category_id
        if asset_category is not None:
            self.asset_category = asset_category
        if asset_maintenance_type is not None:
            self.asset_maintenance_type = asset_maintenance_type
        if links is not None:
            self.links = links
        if embedded is not None:
            self.embedded = embedded

    @property
    def id(self):
        """Gets the id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501


        :return: The id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Assetic3IntegrationRepresentationsMaintenanceAsset.


        :param id: The id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def asset_id(self):
        """Gets the asset_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501


        :return: The asset_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :rtype: str
        """
        return self._asset_id

    @asset_id.setter
    def asset_id(self, asset_id):
        """Sets the asset_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.


        :param asset_id: The asset_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :type: str
        """

        self._asset_id = asset_id

    @property
    def asset_name(self):
        """Gets the asset_name of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501


        :return: The asset_name of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :rtype: str
        """
        return self._asset_name

    @asset_name.setter
    def asset_name(self, asset_name):
        """Sets the asset_name of this Assetic3IntegrationRepresentationsMaintenanceAsset.


        :param asset_name: The asset_name of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :type: str
        """

        self._asset_name = asset_name

    @property
    def work_group_id(self):
        """Gets the work_group_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501


        :return: The work_group_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :rtype: int
        """
        return self._work_group_id

    @work_group_id.setter
    def work_group_id(self, work_group_id):
        """Sets the work_group_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.


        :param work_group_id: The work_group_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :type: int
        """

        self._work_group_id = work_group_id

    @property
    def asset_work_group(self):
        """Gets the asset_work_group of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501


        :return: The asset_work_group of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :rtype: str
        """
        return self._asset_work_group

    @asset_work_group.setter
    def asset_work_group(self, asset_work_group):
        """Sets the asset_work_group of this Assetic3IntegrationRepresentationsMaintenanceAsset.


        :param asset_work_group: The asset_work_group of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :type: str
        """

        self._asset_work_group = asset_work_group

    @property
    def criticality_id(self):
        """Gets the criticality_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501


        :return: The criticality_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :rtype: str
        """
        return self._criticality_id

    @criticality_id.setter
    def criticality_id(self, criticality_id):
        """Sets the criticality_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.


        :param criticality_id: The criticality_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :type: str
        """

        self._criticality_id = criticality_id

    @property
    def asset_criticality(self):
        """Gets the asset_criticality of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501


        :return: The asset_criticality of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :rtype: str
        """
        return self._asset_criticality

    @asset_criticality.setter
    def asset_criticality(self, asset_criticality):
        """Sets the asset_criticality of this Assetic3IntegrationRepresentationsMaintenanceAsset.


        :param asset_criticality: The asset_criticality of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :type: str
        """

        self._asset_criticality = asset_criticality

    @property
    def asset_category_id(self):
        """Gets the asset_category_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501


        :return: The asset_category_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :rtype: str
        """
        return self._asset_category_id

    @asset_category_id.setter
    def asset_category_id(self, asset_category_id):
        """Sets the asset_category_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.


        :param asset_category_id: The asset_category_id of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :type: str
        """

        self._asset_category_id = asset_category_id

    @property
    def asset_category(self):
        """Gets the asset_category of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501


        :return: The asset_category of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :rtype: str
        """
        return self._asset_category

    @asset_category.setter
    def asset_category(self, asset_category):
        """Sets the asset_category of this Assetic3IntegrationRepresentationsMaintenanceAsset.


        :param asset_category: The asset_category of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :type: str
        """

        self._asset_category = asset_category

    @property
    def asset_maintenance_type(self):
        """Gets the asset_maintenance_type of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501


        :return: The asset_maintenance_type of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :rtype: str
        """
        return self._asset_maintenance_type

    @asset_maintenance_type.setter
    def asset_maintenance_type(self, asset_maintenance_type):
        """Sets the asset_maintenance_type of this Assetic3IntegrationRepresentationsMaintenanceAsset.


        :param asset_maintenance_type: The asset_maintenance_type of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :type: str
        """

        self._asset_maintenance_type = asset_maintenance_type

    @property
    def links(self):
        """Gets the links of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501


        :return: The links of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :rtype: list[WebApiHalLink]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this Assetic3IntegrationRepresentationsMaintenanceAsset.


        :param links: The links of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :type: list[WebApiHalLink]
        """

        self._links = links

    @property
    def embedded(self):
        """Gets the embedded of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501


        :return: The embedded of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
        :rtype: list[WebApiHalEmbeddedResource]
        """
        return self._embedded

    @embedded.setter
    def embedded(self, embedded):
        """Sets the embedded of this Assetic3IntegrationRepresentationsMaintenanceAsset.


        :param embedded: The embedded of this Assetic3IntegrationRepresentationsMaintenanceAsset.  # noqa: E501
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
        if issubclass(Assetic3IntegrationRepresentationsMaintenanceAsset, dict):
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
        if not isinstance(other, Assetic3IntegrationRepresentationsMaintenanceAsset):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

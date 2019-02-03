# pylint: disable=C0103
"""
OpenTMI Provider module
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class Provider(BaseApi):
    """
    Provider class. Holds details about who provides DUT's
    """
    def __init__(self, name=None, id_=None, ver=None):
        """
        Constructor for Provider
        :param name: String
        :param id:  String
        :param ver:  String
        """
        super(Provider, self).__init__()
        if name:
            self.name = name
        if id_:
            self.id = id_
        if ver:
            self.ver = ver

    @property
    def name(self):
        """
        Getter for provider name
        :return: String
        """
        return self.get("name")

    @name.setter
    @setter_rules()
    def name(self, value):
        """
        Setter for provider name
        :param value: String
        """
        self.set("name", value)

    @property
    def id(self):
        """
        Getter for provider id
        :return: String
        """
        return self.get("id")

    @id.setter
    @setter_rules()
    def id(self, value):
        """
        Setter for provider id
        :param value: String
        """
        self.set("id", value)

    @property
    def ver(self):
        """
        Getter for provider version
        :return: String
        """
        return self.get("ver")

    @ver.setter
    @setter_rules()
    def ver(self, value):
        """
        Setter for provider version
        :param value: String
        """
        self.set("ver", value)

"""
OpenTMI module for Test Framework
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules

class Framework(BaseApi):
    """
    Framework class
    """
    def __init__(self, name=None, version=None):
        """
        Framework constructor
        :param name: String
        :param version: String
        """
        super(Framework, self).__init__()
        if name:
            self.name = name
        if version:
            self.ver = version

    @property
    def name(self):
        """
        Getter for framework name
        :return: String
        """
        return self.get("name")

    @name.setter
    @setter_rules()
    def name(self, value):
        """
        Setter for framework name
        :param value: String
        """
        self.set("name", value)

    @property
    def version(self):
        """
        Getter for framework version
        :return:
        """
        return self.get("ver")

    @version.setter
    @setter_rules()
    def version(self, value):
        """
        Setter for framework version
        :param value: String
        """
        self.set("ver", value)

"""
OpenTMI module for Target
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class Hardware(BaseApi):
    """
    Target Class
    """

    @property
    def vendor(self):
        """
        Getter for vendor
        :return: String
        """
        return self.get("vendor")

    @vendor.setter
    @setter_rules()
    def vendor(self, value):
        """
        Setter for vendor
        :param value: String
        :return: value
        """
        return self.set("vendor", value)

    @property
    def model(self):
        """
        Getter for model
        :return: String
        """
        return self.get("model")

    @model.setter
    @setter_rules()
    def model(self, value):
        """
        Setter for model
        :param value: String
        :return: value
        """
        return self.set("model", value)

    @property
    def rev(self):
        """
        Getter for model
        :return: String
        """
        return self.get("rev")

    @rev.setter
    @setter_rules()
    def rev(self, value):
        """
        Setter for rev
        :param value: String
        :return: value
        """
        return self.set("rev", value)

    @property
    def meta(self):
        """
        Getter for meta
        :return: String
        """
        return self.get("meta")

    @meta.setter
    @setter_rules()
    def meta(self, value):
        """
        Setter for rev
        :param value: String
        :return: value
        """
        return self.set("meta", value)

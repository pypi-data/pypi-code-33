"""
OpenTMI module for CI details
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class Location(BaseApi):
    """
    Location Class
    """


class Ci(BaseApi):
    """
    CI Class
    """
    def __init__(self, system=None, location=None):
        super(Ci, self).__init__()
        if system:
            self.system = system
        if location:
            self.location = location

    @property
    def system(self):
        """
        Getter for CI System
        :return: String
        """
        return self.get("system")

    @system.setter
    @setter_rules(value_type=str, enum="Jenkins travisCI circleCI")
    def system(self, value):
        """
        Setter for CI system
        :param value: String (Jenkins/travisCI/circleCI)
        :return: value
        """
        return self.set("system", value)

    @property
    def location(self):
        """
        Getter for CI location
        :return:
        """
        return self.get("location")

    @location.setter
    @setter_rules(value_type=Location)
    def location(self, value):
        """
        Setter for CI location
        :param value: Location
        :return: value
        """
        return self.set("location", value)

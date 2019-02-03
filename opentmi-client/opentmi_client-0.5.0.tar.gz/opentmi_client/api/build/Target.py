"""
OpenTMI module for Target
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules
from opentmi_client.api.build.Hardware import Hardware


class Target(BaseApi):
    """
    Target Class
    """
    def __init__(self):
        super(Target, self).__init__()
        self.hardware = Hardware()

    @property
    def type(self):
        """
        Getter for target type
        :return: String
        """
        return self.get("type")

    @type.setter
    @setter_rules(value_type=str, enum="simulate hardware")
    def type(self, value):
        """
        Setter for target type
        :param value: String (simulate/hardware)
        :return: value
        """
        return self.set("type", value)

    @property
    def operating_system(self):
        """
        Getter for target type
        :return: String
        """
        return self.get("os")

    @operating_system.setter
    @setter_rules(value_type=str, enum="win32 win64 unix32 unix64 mbedOS unknown")
    def operating_system(self, value):
        """
        Setter for target os
        :param value: String (win32 win64 unix32 unix64 mbedOS unknown)
        :return: value
        """
        return self.set("os", value)

    @property
    def hardware(self):
        """
        Getter for target hw
        :return: Hardware
        """
        return self.get("hw")

    @hardware.setter
    @setter_rules(value_type=Hardware)
    def hardware(self, value):
        """
        Setter for target hw
        :param value: Hardware
        :return: value
        """
        return self.set("hw", value)

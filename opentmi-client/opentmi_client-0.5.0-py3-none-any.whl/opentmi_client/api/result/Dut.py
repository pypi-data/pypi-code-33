"""
OpentTMI module for DUT (Device under test)
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules
from opentmi_client.api.result.Provider import Provider


class Dut(BaseApi):
    """
    Dut class
    """

    @property
    def count(self):
        """
        Getter for dut count
        :return: Integer
        """
        return self.get("count")

    @count.setter
    @setter_rules(value_type=int)
    def count(self, value):
        """
        Setter for dut count
        :param value: integer
        :return: value
        """
        return self.set("count", value)

    @property
    def type(self):
        """
        Getter for DUT type
        :return: String
        """
        return self.get("type")

    @type.setter
    @setter_rules(enum="hw simulator process")
    def type(self, value):
        """
        Setter for DUT type
        :param value: String, hw|simulator|process
        :return: value
        """
        return self.set("type", value)

    @property
    def ref(self):
        """
        Getter for reference
        :return: String
        """
        return self.get("ref")

    @ref.setter
    @setter_rules()
    def ref(self, value):
        """
        Setter for reference
        :param value:
        :return:
        """
        return self.set("ref", value)

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
        Setter for DUT vendor
        :param value: String
        :return: value
        """
        return self.set("vendor", value)

    @property
    def model(self):
        """
        Getter for dut model
        :return: String
        """
        return self.get("model")

    @model.setter
    @setter_rules()
    def model(self, value):
        """
        Setter for dut model
        :param value: String
        :return: value
        """
        return self.set("model", value)

    @property
    def ver(self):
        """
        Getter for dut version
        :return: String
        """
        return self.get("ver")

    @ver.setter
    @setter_rules()
    def ver(self, value):
        """
        Setter for version
        :param value: String
        :return: value
        """
        return self.set("ver", value)

    @property
    def serial_number(self):
        """
        Getter for dut Serial Number
        :return: String
        """
        return self.get("sn")

    @serial_number.setter
    @setter_rules()
    def serial_number(self, value):
        """
        Setter for Serial Number
        :param value: String
        :return: value
        """
        return self.set("sn", value)

    @property
    def provider(self):
        """
        Getter for dut provider
        :return: String
        """
        return self.get("provider")

    @provider.setter
    @setter_rules(value_type=Provider)
    def provider(self, value):
        """
        Setter for dut provider
        :return: Provider
        """
        return self.set("provider", value)

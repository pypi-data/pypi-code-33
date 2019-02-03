"""
OpenTMI module for Event
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class Ref(BaseApi):
    """
    Ref Class
    """

    @property
    def result(self):
        """
        Getter for result
        :return: String
        """
        return self.get("result")

    @result.setter
    @setter_rules()
    def result(self, value):
        """
        Setter for result
        :param value: string
        :return: Ref
        """
        return self.set("result", value)

    @property
    def testcase(self):
        """
        Getter for testcase
        :return: String
        """
        return self.get("testcase")

    @testcase.setter
    @setter_rules()
    def testcase(self, value):
        """
        Setter for testcase
        :param value: string
        :return: Ref
        """
        return self.set("testcase", value)

    @property
    def resource(self):
        """
        Getter for resource
        :return: String
        """
        return self.get("resource")

    @resource.setter
    @setter_rules()
    def resource(self, value):
        """
        Setter for resource
        :param value: string
        :return: Ref
        """
        return self.set("resource", value)

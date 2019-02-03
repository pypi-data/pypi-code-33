"""
OpenTMI module for Environment details
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules
from opentmi_client.api.result.Framework import Framework

class Environment(BaseApi):
    """
    Environment class
    """
    def __init__(self, framework=None):
        """
        constructor for Environment
        :param framework: String
        """
        super(Environment, self).__init__()
        self.framework = framework if framework else Framework()

    @property
    def ref(self):
        """
        Getter for environment reference
        :return: String
        """
        return self.get("ref")

    @ref.setter
    @setter_rules()
    def ref(self, value):
        self.set("ref", value)

    @property
    def framework(self):
        """
        Getter for framework
        :return: Framework
        """
        return self.get("framework")

    @framework.setter
    @setter_rules(value_type=Framework)
    def framework(self, value):
        self.set("framework", value)

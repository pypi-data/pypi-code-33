"""
OpentTMI module for Priority
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class Priority(BaseApi):
    """
    Priority class
    """

    @property
    def level(self):
        """
        Getter for level
        :return: String
        """
        return self.get("level")

    @level.setter
    @setter_rules(
        enum=['emerg', 'alert', 'crit', 'err',
              'warning', 'notice', 'info', 'debug'])
    def level(self, value):
        """
        Setter for level
        :param value: string
        :return: Priority
        """
        return self.set("level", value)

    @property
    def facility(self):
        """
        Getter for facility
        :return: String
        """
        return self.get("facility")

    @facility.setter
    @setter_rules(
        enum=['auth', 'cron', 'mail', 'news', 'syslog',
              'user', 'result', 'resource', 'testcase'])
    def facility(self, value):
        """
        Setter for facility
        :param value: string
        :return: Priority
        """
        return self.set("facility", value)

# pylint: disable=C0103

"""
OpenTMI module for Test Job
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class Job(BaseApi):
    """
    Job Class
    """
    def __init__(self, id_=None):
        """
        Constructor for Job
        :param id_: String
        """
        super(Job, self).__init__()
        if id_:
            self.id = id_

    @property
    def id(self):
        """
        Getter for job id
        :return: String
        """
        return self.get("id")

    @id.setter
    @setter_rules()
    def id(self, value):
        """
        Setter for Job id
        :param value: String
        """
        self.set("id", value)

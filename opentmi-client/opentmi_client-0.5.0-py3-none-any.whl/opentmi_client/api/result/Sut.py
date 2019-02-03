"""
OpenTMI SUT (Software under test) module
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class Sut(BaseApi):
    """
    SUT (Software Under Test) class
    """

    def __init__(self):
        super(Sut, self).__init__()
        self.set("cut", [])
        self.set("fut", [])

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
        :param value: String
        """
        self.set("ref", value)

    @property
    def cut(self):
        """
        Getter for cut
        :return: String
        """
        return self.get("cut")

    @setter_rules()
    def append_cut(self, value):
        """
        Append one component under test
        :param value: String
        """
        self.cut.append(value)

    @property
    def fut(self):
        """
        Getter for fut
        :return: String
        """
        return self.get("fut")

    @setter_rules()
    def append_fut(self, value):
        """
        Append one feature under test
        :param value: String
        """
        self.get("fut").append(value)


# gitUrl: {type: String, default: ''},
# buildName: {type: String},
# buildDate: {type: Date},
# buildUrl: {type: String, default: ''},
# buildSha1: {type: String},
# branch: {type: String, default: ''},
# commitId: {type: String, default: ''},
# tag: [{type: String}],
# href: {type: String},

"""
OpenTMI module for Test Build
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules
from opentmi_client.api.build.Ci import Ci
from opentmi_client.api.build.Vcs import Vcs
from opentmi_client.api.build.Target import Target


class Build(BaseApi):
    """
    Build class
    """
    def __init__(self,
                 name=None):
        super(Build, self).__init__()
        self.target = Target()
        self.vcs = []
        self.ci_tool = Ci()
        if name:
            self.name = name

    @property
    def name(self):
        """
        Getter for build name
        :return: String
        """
        return self.get("name")

    @name.setter
    @setter_rules()
    def name(self, value):
        """
        Setter for build name
        :param value: String
        :return: value
        """
        self.set("name", value)

    @property
    def type(self):
        """
        Getter for build type
        :return: String
        """
        return self.get("type")

    @type.setter
    @setter_rules(value_type=str, enum="app lib test")
    def type(self, value):
        """
        Setter for build type
        :param value: String (app/lib/test)
        :return: value
        """
        self.set("type", value)

    @property
    def ci_tool(self):
        """
        Getter for CI tool
        :return: Ci
        """
        return self.get("ci")

    @ci_tool.setter
    @setter_rules(value_type=Ci)
    def ci_tool(self, value):
        """
        Getter for CI tool
        :param value: Ci instance
        :return: value
        """
        self.set("ci", value)

    @property
    def vcs(self):
        """
        Getter for VCS
        :return: Vcs
        """
        return self.get("vcs")

    @vcs.setter
    @setter_rules(value_type=list, each_type=Vcs)
    def vcs(self, value):
        """
        Setter for Vcs
        :param value: List<Vcs>
        :return: value
        """
        self.set("vcs", value)

    @property
    def uuid(self):
        """
        Getter for UUID
        :return: String
        """
        return self.get("uuid")

    @uuid.setter
    @setter_rules()
    def uuid(self, value):
        """
        Setter for uuid
        :param value: String
        :return: value
        """
        self.set("uuid", value)

    @property
    def compiled_by(self):
        """
        Getter for compiler-by
        :return: String
        """
        return self.get("compiledBy")

    @compiled_by.setter
    @setter_rules(enum="CI manual")
    def compiled_by(self, value):
        """
        Setter for compiler-by
        :param value: String (CI/manual)
        :return: value
        """
        self.set("compiledBy", value)

    @property
    def change_id(self):
        """
        Getter for change-id
        :return: String
        """
        return self.get("changeId")

    @change_id.setter
    @setter_rules()
    def change_id(self, value):
        """
        Setter for change-id
        :param value: String
        :return: value
        """
        self.set("changeId", value)

    @property
    def target(self):
        """
        Getter for target
        :return: Target
        """
        return self.get("target")

    @target.setter
    @setter_rules(value_type=Target)
    def target(self, value):
        """
        Getter for target
        :param value: Target instance
        :return: value
        """
        self.set("target", value)

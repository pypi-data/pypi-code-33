"""
OpenTMI module for VCS
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class Vcs(BaseApi):
    """
    Version Control System class
    """

    @property
    def name(self):
        """
        Getter for VCS Name
        :return:
        """
        return self.get("name")

    @name.setter
    @setter_rules()
    def name(self, value):
        """
        Setter for VCS name
        :param value: String
        :return: value
        """
        return self.set("name", value)

    @property
    def system(self):
        """
        Getter for VCS system, e.g. git
        :return: String
        """
        return self.get("system")

    @system.setter
    @setter_rules(enum="git SVN CSV")
    def system(self, value):
        """
        Setter for VCS system, e.g. git
        :param value: String
        :return: value
        """
        return self.set("system", value)

    @property
    def type(self):
        """
        Getter for VCS type
        :return: String
        """
        return self.get("type")

    @type.setter
    @setter_rules(enum="PR")
    def type(self, value):
        """
        Setter for VSC type, e.g. PR
        :param value: String
        :return: value
        """
        return self.set("type", value)

    @property
    def commit_id(self):
        """
        Getter for commit id
        :return: String
        """
        return self.get("commitId")

    @commit_id.setter
    @setter_rules()
    def commit_id(self, value):
        """
        Setter for commit id
        :param value: String
        :return: value
        """
        return self.set("commitId", value)

    @property
    def branch(self):
        """
        Getter for branch
        :return: String
        """
        return self.get("branch")

    @branch.setter
    @setter_rules()
    def branch(self, value):
        """
        Setter for Branch
        :param value: String
        :return: value
        """
        return self.set("branch", value)

    @property
    def base_branch(self):
        """
        Getter for base branch
        :return: String
        """
        return self.get("base_branch")

    @base_branch.setter
    @setter_rules()
    def base_branch(self, value):
        """
        Getter for base branch
        :param value: String
        :return: value
        """
        return self.set("base_branch", value)

    @property
    def base_commit(self):
        """
        Getter for base commit
        :return: String
        """
        return self.get("base_commit")

    @base_commit.setter
    @setter_rules()
    def base_commit(self, value):
        """
        Setter for base commit
        :param value: String
        :return: value
        """
        return self.set("base_commit", value)

    @property
    def pr_number(self):
        """
        Getter for PR number
        :return: String
        """
        return self.get("pr_number")

    @pr_number.setter
    @setter_rules()
    def pr_number(self, value):
        """
        Setter for PR number
        :param value: String
        :return: value
        """
        return self.set("pr_number", value)

    @property
    def url(self):
        """
        Getter for url
        :return: String
        """
        return self.get("url")

    @url.setter
    @setter_rules()
    def url(self, value):
        """
        Setter for url
        :param value: String
        :return: value
        """
        return self.set("url", value)

    @property
    def clean_wa(self):
        """
        Getter for clean workarea state
        :return: Boolean
        """
        return self.get("clean_wa")

    @clean_wa.setter
    @setter_rules(value_type=bool)
    def clean_wa(self, value):
        """
        Setter for clean workarea
        :param value: Boolean
        :return: value
        """
        return self.set("clean_wa", value)

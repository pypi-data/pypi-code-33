"""
OpenTMI module for File
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class File(BaseApi):
    """
    File Class
    """

    def __str__(self):
        return "{}".format(self.get("name", "unknown"))

    @property
    def name(self):
        """
        Getter for file name
        :return: String
        """
        return self.get("name")

    @name.setter
    @setter_rules()
    def name(self, value):
        """
        Setter for file name
        :param value: String
        """
        self.set("name", value)

    @property
    def mime_type(self):
        """
        Getter for mime_type
        :return: String
        """
        return self.get("mime_type")

    @mime_type.setter
    @setter_rules()
    def mime_type(self, value):
        """
        Setter for mime_type
        :param value: String
        """
        self.set("mime_type", value)

    @property
    def encoding(self):
        """
        Getter for encoding
        :return: String
        """
        return self.get("encoding")

    @encoding.setter
    @setter_rules(enum='raw base64')
    def encoding(self, value):
        """
        Setter for encoding
        :param value: String
        """
        self.set("encoding", value)

    @property
    def data(self):
        """
        Getter for data
        :return: String
        """
        return self.get("data")

    @data.setter
    @setter_rules(value_type=bytearray)
    def data(self, value):
        """
        Setter for data
        :param value: bytearray
        """
        self.set("data", value)

    def set_file_data(self, value, encoding="raw"):
        """
        Set string data
        :param value: str
        :param encoding: str, "raw" by default
        """
        self.encoding = encoding
        data = bytearray()
        try:
            # python 2
            data.extend(value)
        except TypeError:
            # Python3:
            data.extend(map(ord, value))
        self.data = data

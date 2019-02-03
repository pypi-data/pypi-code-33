"""
OpenTMI module for Event
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules
from opentmi_client.api.event.Priority import Priority
from opentmi_client.api.event.Ref import Ref


class Event(BaseApi):
    """
    Event Class
    """

    def __init__(self):
        """
        Constructor for Event
        """
        super(Event, self).__init__()
        self.priority = Priority()
        self.ref = Ref()

    def __str__(self):
        return "{}".format(self.get("id", "unknown"))

    @property
    def traceid(self):
        """
        Getter for traceid
        :return: String
        """
        return self.get("traceid")

    @traceid.setter
    @setter_rules()
    def traceid(self, value):
        """
        Setter for traceid
        :param value: string
        """
        self.set("traceid", value)

    @property
    def eid(self):
        """
        Getter for event id
        :return: String
        """
        return self.get("id")

    @eid.setter
    @setter_rules()
    def eid(self, value):
        """
        Setter for event id
        :param value: string
        """
        self.set("id", value)

    @property
    def msgid(self):
        """
        Getter for msgid
        :return: String
        """
        return self.get("msgid")

    @msgid.setter
    @setter_rules(
        enum=['ALLOCATED', 'RELEASED', 'ENTER_MAINTENANCE',
              'EXIT_MAINTENANCE', 'CREATED', 'DELETED', 'FLASHED'])
    def msgid(self, value):
        """
        Setter for msgid
        :param value: string
        """
        self.set("msgid", value)

    @property
    def msg(self):
        """
        Getter for msg
        :return: String
        """
        return self.get("msg")

    @msg.setter
    @setter_rules()
    def msg(self, value):
        """
        Setter for msg
        :param value: string
        """
        self.set("msg", value)

    @property
    def tag(self):
        """
        Getter for tag
        :return: String
        """
        return self.get("tag")

    @tag.setter
    @setter_rules()
    def tag(self, value):
        """
        Setter for tag
        :param value: string
        """
        self.set("tag", value)

    @property
    def duration(self):
        """
        Getter for duration
        :return: float
        """
        return self.get("duration")

    @duration.setter
    @setter_rules(value_type=float)
    def duration(self, value):
        """
        Setter for duration
        :param value: float
        """
        self.set("duration", value)

    @property
    def spare(self):
        """
        Getter for spare
        :return: String
        """
        return self.get("spare")

    @spare.setter
    def spare(self, value):
        """
        Setter for spare
        :param value: *
        """
        self.set("spare", value)

    @property
    def priority(self):
        """
        Getter for priority
        :return: Priority
        """
        return self.get("priority")

    @priority.setter
    @setter_rules(value_type=Priority)
    def priority(self, value):
        """
        Setter for priority
        :param value: Priority
        """
        self.set("priority", value)

    @property
    def ref(self):
        """
        Getter for ref
        :return: Ref
        """
        return self.get("ref")

    @ref.setter
    @setter_rules(value_type=Ref)
    def ref(self, value):
        """
        Setter for ref
        :param value: Ref
        """
        self.set("ref", value)

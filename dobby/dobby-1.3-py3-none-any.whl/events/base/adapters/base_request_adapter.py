from dobby.events.base.requests.base_request import BaseRequest


class BaseRequestAdapter:
    """A base class for all request adapter"""

    def __init__(self):
        pass

    def translate(self, event, context):
        """The translation method that map event and context to the correspondent request type. """

        return BaseRequest()

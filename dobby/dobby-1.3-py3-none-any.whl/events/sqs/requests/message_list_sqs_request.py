from dobby.events.base.requests.base_request import BaseRequest


class MessageListSQSRequest(BaseRequest):
    """SQS request class containing only the list of decoded messages"""

    def __init__(self, messages):

        super().__init__(data=messages)

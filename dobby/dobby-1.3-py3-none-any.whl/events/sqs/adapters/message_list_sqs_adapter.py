import json

from dobby.events.base.adapters.base_request_adapter import BaseRequestAdapter
from dobby.events.sqs.requests.message_list_sqs_request import MessageListSQSRequest


class MessageListSqsRequestAdapter(BaseRequestAdapter):
    """
        An adapter for SQS events that constructs the request using only the 
        decoded bodies of the messages
    """

    __RECORDS_KEY = 'Records'

    def __init__(self):
        BaseRequestAdapter.__init__(self)

    def translate(self, event, context):

        records = event[self.__RECORDS_KEY]
        messages = list(map(
            lambda m: json.loads(m['body']),
            records
        ))

        return MessageListSQSRequest(messages)

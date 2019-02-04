import json

import boto3

from pyqalx.core.entity import QalxEntity
from pyqalx.core.errors import QalxQueueError
from pyqalx.core.group import Group
from pyqalx.core.item import Item
from pyqalx.core.set import Set


class QueueResponse:
    """a response from a remote queue"""

    def __init__(self, response):
        """make new response

        v0.1 - doesn't do much yet
        :param response: response from queue
        """
        self._raw_response = response


class QueueMessage:
    """a message frm the queue

    attributes:
        body: message body
        receipt_handle: some information to return to the message broker to confirm receipt
    """

    def __init__(self, message):
        """

        :param message: the full raw message from the queue
        """
        self._raw_message = message
        self.body = json.loads(message['Body'])
        self.receipt_handle = message['ReceiptHandle']


class Queue(QalxEntity):
    """QalxEntity with entity_type Queue

    attributes:
        broker_client: an authenticated client to communicate with the remote message broker
    """
    entity_type = 'queue'

    def _stringify(self, message: dict) -> str:
        return json.dumps(message)

    def __init__(self, *args, **kwargs):
        super(Queue, self).__init__(*args, **kwargs)

        if self.get('info') and ('credentials' in self['info']):
            self.broker_client = boto3.client('sqs',
                                              region_name="eu-west-2",  # TODO: make this configurable
                                              aws_access_key_id=self['info']['credentials']['ACCESS_KEY_ID'],
                                              aws_secret_access_key=self['info']['credentials']['SECRET_ACCESS_KEY'],
                                              aws_session_token=self['info']['credentials']['SESSION_TOKEN'])
        else:
            self.broker_client = None

    def submit_sets_from_group(self, group):
        """

        :param group: a group
        :type group: pyqalx.core.Group
        :returns: pyqalx.core.queue.QueueResponse
        """
        entries = []
        for n, set_guid in enumerate(group['set_guids']):
            entries.append(
                {
                    "Id": str(n),
                    'MessageBody': json.dumps({
                        "entity_type": "set",
                        "entity_guid": set_guid,
                        "parent_group_guid": group['guid']
                    })
                })
        response = self.broker_client.send_message_batch(
            QueueUrl=self['info']['queue_url'],
            Entries=entries
        )
        return QueueResponse(response)

    def get_messages(self, max_num_msg, visibility, waittime):
        """get messages from the queue

        :param max_num_msg: maximum number to retrieve
        :param visibility: time in seconds until the message becomes visible again on the queue
        :param waittime: time to wait for a message
        :return: list of pyqalx.core.queue.QueueMessage
        """
        responses = self.broker_client.receive_message(
            QueueUrl=self['info']['queue_url'],
            MaxNumberOfMessages=max_num_msg,
            VisibilityTimeout=visibility,
            WaitTimeSeconds=waittime,
        )
        if not responses.get("Messages"):
            return []
        else:
            return [QueueMessage(response) for response in responses['Messages']]

    def delete_message(self, message):
        """remove message from the queue

        :param message:
        :type message QalxMessage
        :return:
        """
        self.broker_client.delete_message(
            QueueUrl=self['info']['queue_url'],
            ReceiptHandle=message.receipt_handle
        )

    def submit_entity(self, entity):
        """put a qalx entity on the queue

        :param entity: entity to add to the queue
        :type entity: pyqalx.core.entity.QalxEntity
        :return: pyqalx.core.queue.QueueResponse
        """
        if not type(entity) in [Item, Set, Group]:
            raise QalxQueueError("Only Item, Set and Group entities can be submitted to the queue.")
        response = self.broker_client.send_message(QueueUrl=self['info']['queue_url'],
                                                   MessageBody=self._stringify(
                                                       {"entity_type": entity.entity_type,
                                                        "entity_guid": entity['guid']
                                                        }))
        return QueueResponse(response)

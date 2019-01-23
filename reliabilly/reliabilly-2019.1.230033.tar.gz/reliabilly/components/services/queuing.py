# pylint: disable=invalid-name,broad-except
import base64
import json
import uuid
from functools import partial
import botocore
from boto3 import resource, client
from nameko.extensions import Entrypoint
from reliabilly.components.logger import Logger
from reliabilly.settings import Constants, Settings


def get_sqs_client(endpoint_url):
    config = botocore.client.Config(connect_timeout=1, read_timeout=1)
    if not endpoint_url:
        return client(Constants.SQS_CLIENT, region_name=Settings.AWS_REGION, config=config)
    return client(Constants.SQS_CLIENT, endpoint_url=endpoint_url, region_name=Settings.AWS_REGION, config=config)


def get_sqs_resource(endpoint_url):
    config = botocore.client.Config(connect_timeout=1, read_timeout=1)
    if not endpoint_url:
        return resource(Constants.SQS_CLIENT, region_name=Settings.AWS_REGION, config=config)
    return resource(Constants.SQS_CLIENT, endpoint_url=endpoint_url, region_name=Settings.AWS_REGION, config=config)


def get_encoded_string(message: str, encoding=Constants.UTF8) -> str:
    return base64.b64encode(message.encode(encoding)).decode(encoding)


def get_decoded_string(message: str, encoding=Constants.UTF8) -> str:
    message += Constants.EQUAL * ((4 - len(message) % 4) % 4)  # pad the message with = if needed
    return base64.b64decode(message).decode(encoding)


class QueueMessage:  # pylint: disable=too-many-instance-attributes
    receipt_handle: str = Constants.EMPTY
    message_id: str = Constants.EMPTY

    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        if not self.message_id:
            self.message_id = str(uuid.uuid4())

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str(self.__dict__)

    @property
    def body(self):
        return get_encoded_string(json.dumps(self.__dict__, default=str))

    @staticmethod
    def create_from_encoded(encoded_message: str):
        message_string = get_decoded_string(encoded_message)
        message = json.loads(message_string)
        return QueueMessage(**message)


class MessageQueue:
    def __init__(self, **kwargs):
        self.logger = kwargs.get(Constants.LOGGER, Logger())
        self.queue_name = kwargs.get(Constants.QUEUE_NAME, None)
        self.endpoint_url = None
        if not Settings.ENV:
            self.endpoint_url = kwargs.get(Constants.ENDPOINT_URL, f'{Settings.SQS_URL}:{Settings.SQS_PORT}')
        self.sqs_resource = kwargs.get(Constants.CLIENT, get_sqs_resource(self.endpoint_url))
        self.sqs_client = kwargs.get(Constants.CLIENT, get_sqs_client(self.endpoint_url))

    def send_message(self, message: QueueMessage):
        try:
            self.logger.info(f'Sending message Id: {message.message_id} Body: {message}')
            sqs_queue = self.create_queue(self.queue_name)
            sqs_queue.send_message(MessageBody=message.body)
            self.logger.info(f'Sent message Id: {message.message_id} Body: {message}')
            return True
        except Exception as ex:
            self.logger.error(f'Error sending message Id: {message.message_id} to queue: {self.queue_name} ex: {ex}')
            return False

    def receive_message(self, wait_seconds: int = Constants.DEFAULT_MESSAGE_WAIT_SECONDS) -> QueueMessage:
        message_id = None
        queue_message = None
        try:
            sqs_queue = self._get_queue(self.queue_name)
            response = self.sqs_client.receive_message(QueueUrl=sqs_queue.url, WaitTimeSeconds=wait_seconds)
            messages = response.get(Constants.MESSAGES_KEY, ())
            for message in messages:
                message_body = message[Constants.BODY_KEY]
                self.logger.info(f'Received raw message from queue {message_body}.')
                queue_message = QueueMessage.create_from_encoded(message_body)
                queue_message.receipt_handle = message[Constants.RECEIPT_HANDLE_KEY]
                message_id = queue_message.message_id
                self.logger.info(f'Received message Id:{message_id} from queue {self.queue_name}.')
                return queue_message
        except Exception as ex:
            if Constants.TIMEOUT not in str(ex):  # The receive message will timeout when there is no message
                self.logger.error(f'Error receiving message from queue {self.queue_name}. Id:{message_id} ex: {ex}')
        return queue_message

    def complete_message(self, message):
        try:
            sqs_queue = self._get_queue(self.queue_name)
            self.sqs_client.delete_message(QueueUrl=sqs_queue.url, ReceiptHandle=message.receipt_handle)
            return True
        except Exception as ex:
            self.logger.error(f'Error completing message {message} on queue. ex: {ex}')
            return False

    def purge(self):
        try:
            sqs_queue = self._get_queue(self.queue_name)
            self.sqs_client.purge_queue(QueueUrl=sqs_queue.url)
            return True
        except Exception as ex:
            self.logger.error(f'Error purging queue {self.queue_name}. ex: {ex}')
            return False

    def create_queue(self, queue_name):
        if not self.sqs_client or not queue_name:
            return None
        sqs_queue = self._get_queue(queue_name)
        if not sqs_queue:
            try:
                self.logger.info(f'Creating sqs queue {queue_name}...')
                sqs_queue = self.sqs_resource.create_queue(
                    QueueName=queue_name, Attributes=Constants.SQS_CREATION_ATTRIBUTES)
                self.sqs_resource.tag_queue(QueueUrl=sqs_queue.url, Tags=Constants.RESOURCE_TAGS)
            except Exception as ex:
                self.logger.info(f'Error calling create_queue {queue_name}. ex: {ex}')
        return sqs_queue

    def _get_queue(self, queue_name):
        try:
            return self.sqs_resource.get_queue_by_name(QueueName=queue_name)
        except Exception as ex:
            self.logger.info(f'Error calling get_queue_by_name {queue_name}. ex: {ex}')
            return None


# noinspection PyArgumentList
class SqsReceiver(Entrypoint):

    def __init__(self, queue_name, **kwargs):
        self.queue_name = queue_name
        self.runner = True
        self.exit = False
        self.client = kwargs.pop(Constants.CLIENT, MessageQueue(queue_name=self.queue_name))
        self.logger = kwargs.pop(Constants.LOGGER, Logger())
        super().__init__(**kwargs)

    def setup(self):
        try:
            self.client.create_queue(self.queue_name)
        except Exception as ex:
            self.logger.info(f'Setup of sqs entrypoint failed for queue {self.queue_name}. {ex}')

    def start(self):
        self.container.spawn_managed_thread(self.run, identifier=Constants.QUEUE_RECEIVER_ID)

    def run(self, receive_func=None):
        if not receive_func:
            receive_func = self.receive_message
        while self.runner:
            receive_func()
            if self.exit:
                break
        return True

    def receive_message(self):
        try:
            message = self.client.receive_message()
            if message:
                self.handle_message(message)
        except Exception as ex:
            self.logger.error(f'Error receiving queue message in nameko entrypoint. ex: {ex}')

    def handle_message(self, message):
        if not message:
            return
        handle_result = partial(self.handle_result, message)
        args = (message,)
        self.container.spawn_worker(self, args, {}, handle_result=handle_result)

    def handle_result(self, message, _, result, exc_info):
        self.client.complete_message(message)
        return result, exc_info


queue = SqsReceiver.decorator

import json
import logging

import arrow
import boto3
import rollbar

from . import _collector as collector
from . import exceptions, models, utils


logger = logging.getLogger(__name__)

NOT_PROVIDED = object()


class Consumer:
    def __init__(self, queue_name: str, handlers: dict):
        self._queue_name = queue_name
        self._queue_full_name = utils.construct_full_queue_name(queue_name)
        self._handlers = handlers

    @property
    def queue(self):
        if not hasattr(self, "_queue"):
            sqs = boto3.resource("sqs")
            self._queue = sqs.get_queue_by_name(QueueName=self._queue_full_name)
        return self._queue

    @property
    def dead_letter_queue(self):
        """
        Find the dead letter queue from the primary queue's redrive policy.

        https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html
        """

        if not hasattr(self, "_dead_letter_queue"):
            try:
                redrive_policy = json.loads(self.queue.attributes["RedrivePolicy"])
                dlq_name = redrive_policy["deadLetterTargetArn"].split(":")[-1]
            except Exception as e:
                raise exceptions.ConsumerException(
                    f"No dead letter queue configured for {self.queue}"
                ) from e

            sqs = boto3.resource("sqs")
            self._dead_letter_queue = sqs.get_queue_by_name(QueueName=dlq_name)
        return self._dead_letter_queue

    def process_queue(self):
        collector.increment("consumer.attempt_read", tags={"queue": self._queue_name})
        messages = self.queue.receive_messages(WaitTimeSeconds=5, MaxNumberOfMessages=10)
        if len(messages) > 0:
            logger.info(f"Received {len(messages)} messages")

        for message in messages:
            try:
                body = json.loads(message.body)
                data = json.loads(body["Message"])
                message_type = data["message_type"]
                payload = data["payload"]
            except Exception:
                rollbar.report_exc_info()
                continue
            try:
                handler = self._handlers.get(message_type)
                if handler:
                    logger.info(f"Processing {message_type} message")
                    handler(payload)
                    result = "succeeded"
                    logger.info(f"Done processing {message_type} message")

                else:
                    result = "skipped"
                    logger.info(f"Received unregistered message_type: {message_type}")
            except Exception:
                result = "failed"
                uuid = rollbar.report_exc_info()  # is None on local container test
                messageId = body["MessageId"]
                url = f"https://rollbar.com/item/uuid/?uuid={uuid}"
                logger.exception(
                    f"An error occurred while processing the "
                    f"message. MessageId: {messageId} Rollbar URL: {url}"
                )
            else:
                message.delete()

            collector.increment(
                "consumer.processed",
                tags={"result": result, "message_type": message_type, "queue": self._queue_name},
            )

    def process_dead_letter_queue(self):
        messages = self.dead_letter_queue.receive_messages(
            WaitTimeSeconds=0, MaxNumberOfMessages=10
        )
        if len(messages) > 0:
            logger.info(f"Received {len(messages)} messages on the dead letter queue")

        for message in messages:
            body = json.loads(message.body)
            data = json.loads(body["Message"])
            models.UndeliverableMessage.objects.create(
                message_type=data["message_type"],
                message_timestamp=arrow.get(body["Timestamp"]).datetime,
                payload=message.body,
                queue=self._queue_name,
                topic_arn=body.get("TopicArn"),
            )
            message.delete()

    def replay_dead_letter_queue(self, max_messages: int):
        if max_messages < 1:
            raise exceptions.ConsumerException("max_messages must be greater than 0")

        logger.info(
            f"Replaying at most {max_messages} messages "
            f"from {self.dead_letter_queue} to {self.queue}"
        )

        messages_processed = 0
        while True:
            messages = self.dead_letter_queue.receive_messages(
                WaitTimeSeconds=20, MaxNumberOfMessages=10
            )

            for message in messages:
                self.queue.send_message(MessageBody=message.body)
                message.delete()
                messages_processed += 1

                if messages_processed >= max_messages:
                    return

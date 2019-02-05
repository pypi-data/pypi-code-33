import json

from amqpstorm import Message

from .cqrs import Event, MiddlewareBase


def AmqpPublisherMiddleware(
    routing_key: str, exchange: str, infrastructure_name: str = "amqp"
):
    """Return  `_AMQPPublisherClass` instantiated given params.

    :param routing_key: routing  key for message
    :type routing_key: str
    :param exchange: exchange to publish to
    :type exchange: str
    :param infrastructure_name: name of amqp infrastructure, defaults to "amqp"
    :type infrastructure_name: str, optional
    :return: _AMQPPublisher middleware
    :rtype: _AMQPPublisher
    """

    class _AMQPPublisher(MiddlewareBase):
        """Publish `Event` to AMQP exchange."""

        def __call__(self, func, event: Event):
            func()

            self.channel = self.infrastructure_factory.get_infrastructure(
                context=event.context, infrastructure_name=infrastructure_name
            )

            timer = self.statsd.get_timer(event.domain)
            with timer.time(f"publish_amqp_event_time"):
                properties = {"content_type": "application/json"}
                event_content = json.dumps(
                    {
                        "id": str(event.uuid),
                        "parameters": event.parameters,
                        "name": event.event_name,
                        "domain": event.domain,
                        "context": event.context,
                        "user_uuid": event.user_uuid,
                        "created_date": event.created_date,
                    },
                    sort_keys=True,
                )
                message = Message.create(
                    channel=self.channel,
                    body=event_content,
                    properties=properties,
                )
                message.publish(routing_key=routing_key, exchange=exchange)

            self.statsd.get_counter().increment("publish_amqp_event")

    return _AMQPPublisher

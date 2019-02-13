import json

from amqpstorm import Message

from .cqrs import Event, MiddlewareBase


def AmqpPublisherMiddleware(
    publisher_name: str, infrastructure_name: str = "amqp"
):
    """Return  `_AMQPPublisherClass` instantiated given params.

    :param publisher_name: name of publisher to get from config
    :type publisher_name: str
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
            config = self.infrastructure_factory.get_config(
                context=event.context
            )
            publish_settings = config[infrastructure_name]["publish_settings"][
                publisher_name
            ]
            routing_key_prefix = publish_settings["routing_key_prefix"]
            exchange = publish_settings["exchange"]

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

                routing_key = f"{routing_key_prefix}.{event.event_name}"
                message.publish(routing_key=routing_key, exchange=exchange)

            self.statsd.get_counter().increment("publish_amqp_event")

    return _AMQPPublisher

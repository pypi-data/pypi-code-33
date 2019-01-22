"""Tests for Event Publisher module"""
import pytest
from opentracing.propagation import Format

from zeel_publisher.event_publisher import CarrierError
from zeel_publisher.event_publisher import EventPublisher
from zeel_publisher.event_publisher import validate_carrier


@pytest.fixture()
def topic_arn(sns_client):
    """
    Create a new test SNS topic. Delete the created test topic once tests have
    finished executing.
    """

    topic_name = 'test-publisher-topic'
    response = sns_client.create_topic(Name=topic_name)
    yield response.get('TopicArn')
    sns_client.delete_topic(TopicArn=response.get('TopicArn'))


@pytest.fixture()
def event_publisher(config, topic_arn):
    """
    Setup a publisher instance for testing.
    """

    publisher = EventPublisher(
        topic_arn=topic_arn,
        sns_client_params=config.SNS_CLIENT_KWARGS
    )
    return publisher


def test_validate(jaeger_tracer):
    """
    Test that a valid carrier is designated as valid.
    """

    span = jaeger_tracer.start_span('test_span')
    carrier = {}
    jaeger_tracer.inject(
        span_context=span,
        format=Format.TEXT_MAP,
        carrier=carrier
    )
    actual = validate_carrier(carrier)
    assert actual is True


def test_validate_invalid_carrier():
    """
    Test that an invalid carrier raises a CarrierError exception.
    """

    carrier = {}
    actual = validate_carrier(carrier)
    assert actual is False


def test_publish_invalid_carrier(event_publisher):
    """
    Test that a message with an invalid carrier object raises a CarrierError
    exception.
    """

    with pytest.raises(CarrierError):
        carrier = {}
        actual = event_publisher.publish(
            carrier=carrier,
            uri='/orders',
            operation='CREATE',
            before={},
            after={
                'order_id': '456'
            },
            service='zapi-orders',
            description='Order Created',
            triggering_account={
                'account_id': '123'
            },
            triggering_identity={
                'identity_id': '456'
            }
        )
        assert actual is None


def test_publish(jaeger_tracer, event_publisher):
    """
    Test publishing a message and getting a response with a valid MessageId key
    value.
    """

    span = jaeger_tracer.start_span('create_order')
    span.set_tag('order_id', '456')
    carrier = {}
    jaeger_tracer.inject(
        span_context=span,
        format=Format.TEXT_MAP,
        carrier=carrier
    )
    actual = event_publisher.publish(
        carrier=carrier,
        uri='/orders',
        operation='CREATE',
        before=None,
        after={
            'order_id': '456',
            'items': []
        },
        service='zapi-orders',
        description='API - Order Created',
        triggering_account={
            'account_id': '123',
            'label': 'Zeel Inc.'
        },
        triggering_identity={
            'identity_id': '456',
            'first_name': 'Julian',
            'last_name': 'Raymar'
        }
    )
    assert actual.get('MessageId')

"""Tests for sns interface module"""
import pytest

from zeel_publisher.sns import create_topic, subscribe_queue


@pytest.fixture()
def topic_name(sns_client):
    """Create a topic name to use for creating an sns topic"""
    name = 'hot-topic'
    yield name
    arn = 'arn:aws:sns:us-east-1:123456789012:{}'.format(name)
    sns_client.delete_topic(TopicArn=arn)


@pytest.fixture()
def topic_arn(sns_client):
    """Create sns topic and return its arn"""
    topic_name = 'topicana-orange-juice'
    response = sns_client.create_topic(Name=topic_name)
    yield response.get('TopicArn')
    sns_client.delete_topic(TopicArn=response.get('TopicArn'))


@pytest.fixture()
def queue_arn(sqs_client):
    """Create sqs queue and return its arn"""
    queue_name = 'queue-pasa'
    response = sqs_client.create_queue(QueueName=queue_name)
    url = response.get('QueueUrl')

    response = sqs_client.get_queue_attributes(
        QueueUrl=url, AttributeNames=['All'])
    arn = response.get('Attributes').get('QueueArn')
    yield arn
    sqs_client.delete_queue(QueueUrl=url)


def test_create_topic(config, sns_client, topic_name):
    """
    Test that create_topic successfully creates a SNS topic and returns a SNS
    topic ARN.
    """

    topic_arn = create_topic(
        topic_name=topic_name, client_args=config.SNS_CLIENT_KWARGS)

    response = sns_client.list_topics()
    topic = next(
        filter(lambda topic: topic.get('TopicArn') == topic_arn,
               response.get('Topics')))

    assert topic_arn == topic.get('TopicArn')


def test_subscribe_queue(config, sns_client, topic_arn, queue_arn):
    """
    Test that subscribe_queue successfully creates a SQS queue to a SNS topic
    and returns the subscription ARN
    """

    subscription_arn = subscribe_queue(
        topic_arn=topic_arn,
        queue_arn=queue_arn,
        client_args=config.SNS_CLIENT_KWARGS)

    response = sns_client.list_subscriptions()
    subscription = next(
        filter(
            lambda subscription: subscription.get('SubscriptionArn') ==
            subscription_arn, response.get('Subscriptions')))

    assert subscription_arn == subscription.get('SubscriptionArn')

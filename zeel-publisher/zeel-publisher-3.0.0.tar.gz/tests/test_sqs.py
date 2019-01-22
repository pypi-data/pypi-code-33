"""Tests for sqs interface module"""
import pytest

from zeel_publisher.sqs import create_queue


@pytest.fixture()
def queue_name(sqs_client):
    """Create queue name"""
    name = 'baby-you-got-a-queue-going'
    yield name
    url = 'http://localhost:4576/queue/{}'.format(name)
    sqs_client.delete_queue(QueueUrl=url)


def test_create_queue(config, sqs_client, queue_name):
    """
    Test that create_topic successfully creates a SNS topic and returns a SNS
    topic ARN.
    """

    queue_arn = create_queue(
        queue_name=queue_name, client_args=config.SQS_CLIENT_KWARGS)

    response = sqs_client.list_queues(QueueNamePrefix=queue_name)

    url = response.get('QueueUrls')[0]

    response = sqs_client.get_queue_attributes(
        QueueUrl=url, AttributeNames=['All'])

    assert queue_arn == response.get('Attributes').get('QueueArn')

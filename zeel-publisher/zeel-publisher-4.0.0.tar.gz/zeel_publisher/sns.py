"""Helper module for SNS functions"""
import boto3


def create_topic(topic_name, client_args):
    """
    Create a single SNS topic from the provided name.

    Parameters
    ----------
    topic_name : string
        The name of the topic to be created
    client_args : dict
        Parameters needed to create a boto3 SNS client

    Returns
    -------
    mixed
        The arn of the SNS topic if created, null otherwise
    """

    sns_client = boto3.client('sns', **client_args)

    response = sns_client.create_topic(Name=topic_name)

    return response.get('TopicArn')


def subscribe_queue(topic_arn, queue_arn, client_args):
    """
    Subscribe a single SQS queue to a single SNS topic

    Parameters
    ----------
    topic_arn : string
        The arn of the SNS topic to subscribe to
    queue_arn : string
        The arn of the sqs queue to be subscribed
    client_args : dict
        Parameters needed to create a boto3 SNS client

    Returns
    -------
    mixed
        The arn of the subscription if subscribed successfully, null otherwise
    """

    sns_client = boto3.client('sns', **client_args)

    response = sns_client.subscribe(
        Protocol='sqs', TopicArn=topic_arn, Endpoint=queue_arn)

    return response.get('SubscriptionArn')

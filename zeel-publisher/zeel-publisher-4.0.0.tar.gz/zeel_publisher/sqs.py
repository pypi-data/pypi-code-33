"""Helper module for SQS functions"""
import boto3


def create_queue(queue_name, client_args):
    """
    Create a single SQS queue from the provided name.

    Parameters
    ----------
    queue_name : string
        The name of the queue to be created.
    client_args : dict
        Parameters needed to create a boto3 SQS client

    Returns
    -------
    mixed
        The arn of the SQS queue if created successfully, null otherwise
    """

    sqs_client = boto3.client('sqs', **client_args)

    response = sqs_client.create_queue(QueueName=queue_name)
    url = response.get('QueueUrl')

    response = sqs_client.get_queue_attributes(
        QueueUrl=url, AttributeNames=['All'])
    arn = response.get('Attributes').get('QueueArn')

    return arn

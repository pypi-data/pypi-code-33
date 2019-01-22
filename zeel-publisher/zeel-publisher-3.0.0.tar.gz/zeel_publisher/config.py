"""Safe configuration defaults"""
import os

IN_DOCKER = True if os.getenv('AWS_EXECUTION_ENV', False) else False


class Config(object):
    """Base Config class to be inherited by other runtime configs"""
    DEBUG = False
    TESTING = False
    JAEGER_PARAMS = {
        'sampler': {
            'type': 'const',
            'param': 1
        },
        'logging': True,
        'local_agent': {
            'reporting_host': 'jaeger'
        }
    }


class TestingConfig(Config):
    """Config to be used by pytest"""
    AWS_ENDPOINT_HOST = 'localstack' if IN_DOCKER else 'localhost'
    AWS_ENDPOINT_URL = 'http://{}'.format(AWS_ENDPOINT_HOST)
    AWS_REGION = 'us-east-1'

    SNS_TOPIC_NAME = 'test-publisher-topic'
    SNS_CLIENT_KWARGS = {
        'endpoint_url': '{}:4575'.format(AWS_ENDPOINT_URL),
        'region_name': AWS_REGION,
        'aws_access_key_id': 'abc',
        'aws_secret_access_key': '123'
    }

    SQS_QUEUE_NAME = 'test-publisher-queue'
    SQS_CLIENT_KWARGS = {
        'endpoint_url': '{}:4576'.format(AWS_ENDPOINT_URL),
        'region_name': AWS_REGION,
        'aws_access_key_id': 'abc',
        'aws_secret_access_key': '123'
    }

    TESTING = True
    DEBUG = True

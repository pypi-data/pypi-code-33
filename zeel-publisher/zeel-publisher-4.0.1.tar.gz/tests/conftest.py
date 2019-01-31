"""Global test fixtures"""
import pytest
import boto3
import jaeger_client
from zeel_publisher.config import TestingConfig


@pytest.fixture(scope='session')
def config():
    """Create and return an instance of TestingConfig"""
    return TestingConfig()


@pytest.fixture(scope='session')
def sqs_client(config):
    """Create and return a SQS client instance."""
    sqs_client = boto3.client('sqs', **config.SQS_CLIENT_KWARGS)
    return sqs_client


@pytest.fixture(scope='session')
def sns_client(config):
    """Create and return an SNS client instance."""
    sns_client = boto3.client('sns', **config.SNS_CLIENT_KWARGS)
    return sns_client


@pytest.fixture(scope='session')
def jaeger_tracer():
    """
    Setup a jaeger tracer for creating spans. Scope is session level as there
    should only be a single jaeger_tracer instance (Subsequent tracer instances
    after the first initialize to None).
    """

    jaeger_config = jaeger_client.Config(
        config={}, service_name='service_name')
    jaeger_tracer = jaeger_config.initialize_tracer()
    return jaeger_tracer

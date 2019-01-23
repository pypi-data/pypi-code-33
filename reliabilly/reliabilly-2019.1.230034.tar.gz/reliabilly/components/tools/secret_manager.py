import boto3
from botocore.exceptions import ClientError
from reliabilly.components.logger import LoggingProvider
from reliabilly.settings import Settings


def get_default_secret_manager():
    return boto3.client('secretsmanager', region_name=Settings.AWS_REGION)


# pylint: disable=too-few-public-methods
class SecretManager:
    def __init__(self, client=get_default_secret_manager(), logger=LoggingProvider(__name__)):
        self.logger = logger
        self.client = client

    def get_secret(self, secret_key):
        try:
            response = self.client.get_secret_value(SecretId=secret_key)
            return response['SecretString']
        except (ClientError, Exception) as ex:  # pylint: disable=broad-except
            self.logger.error(ex)
            return None

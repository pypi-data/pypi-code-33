import os

import boto3
from boto3.exceptions import S3UploadFailedError
from botocore.exceptions import ClientError

from onepanel.utilities.s3.authentication import Provider


class Wrapper:
    @staticmethod
    def is_error_expired_token(error):
        """
        :param error:
        :type error ClientError
        :return:
        """

        return error.response['Error']['Code'] == 'ExpiredToken'

    def __init__(self, bucket_name=None, credentials_provider=None, retry=3):
        """
        :param bucket: AWS S3 Bucket name
        :param credentials_provider: Provides credentials for requests.
        :type credentials_provider: onepanel.lib.s3.authentication.Provider
        """
        if bucket_name is None:
            bucket_name = os.getenv('DATASET_BUCKET', 'onepanel-datasets')

        if credentials_provider is None:
            credentials_provider = Provider()

        self.bucket_name = bucket_name
        self.credentials_provider = credentials_provider
        self.s3 = None
        self.reset_client()
        self.retry = retry
        self.retries = 0

    def create_client(self):
        if not self.credentials_provider.loads_credentials():
            return boto3.client('s3')

        credentials = self.credentials_provider.credentials()

        return boto3.client('s3',
                            aws_access_key_id=credentials.access_key_id,
                            aws_secret_access_key=credentials.secret_access_key,
                            aws_session_token=credentials.session_token)

    def create_resource(self):
        if not self.credentials_provider.loads_credentials():
            return boto3.resource('s3')

        credentials = self.credentials_provider.credentials()

        return boto3.resource('s3',
                            aws_access_key_id=credentials.access_key_id,
                            aws_secret_access_key=credentials.secret_access_key,
                            aws_session_token=credentials.session_token)

    def reset_client(self):
        self.s3 = self.create_client()

    def list_files(self, prefix):
        paginator = self.s3.get_paginator('list_objects_v2')

        has_more = True
        next_marker = ''

        files = {}

        while has_more:
            response_iterator = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=prefix,
                StartAfter=next_marker,
                PaginationConfig={
                    'MaxItems': 1000,
                    'PageSize': 1000
                }
            )

            content_length = 0

            try:
                for page in response_iterator:
                    if 'Contents' in page:
                        for content in page['Contents']:
                            key = content['Key']
                            files[key] = content
                            next_marker = key
                            content_length += 1
            except ClientError as clientError:
                if Wrapper.is_error_expired_token(clientError) and self.retries < self.retry:
                    self.retries += 1
                    self.reset_client()
                    return self.list_files(prefix)

                self.retries = 0
                raise

            if content_length == 0:
                has_more = False
                break

        # Skip the file that has the same name as the prefix.
        if prefix in files:
            del files[prefix]

        self.retries = 0
        return files

    def upload_file(self, filepath, key):
        # Normalize s3 path if we're on windows
        key = key.replace('\\', '/')

        try:
            result = self.s3.upload_file(filepath, self.bucket_name, key)
            self.retries = 0
            return result
        except ClientError as clientError:
            if Wrapper.is_error_expired_token(clientError) and self.retries < self.retry:
                self.retries += 1
                self.reset_client()
                return self.upload_file(filepath, key)

            raise
        except S3UploadFailedError as uploadError:
            if self.retries < self.retry:
                self.retries += 1
                self.reset_client()
                return self.upload_file(filepath, key)

            raise
        except FileNotFoundError as fileNotFoundError:
            # Do nothing
            return

    def download_file(self, local_path, key):
        s3 = self.create_resource()

        try:
            # Create the directory locally if it doesn't exist yet.
            dirname = os.path.dirname(local_path)
            os.makedirs(dirname, exist_ok=True)
            s3.Bucket(self.bucket_name).download_file(key, local_path)
        except ClientError as clientError:
            if self.retries < self.retry:
                self.retries += 1
                self.reset_client()
                return self.download_file(local_path, key)

            raise

    def delete_file(self, key):
        key = key.replace('\\', '/')

        try:
            result = self.s3.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )

            self.retries = 0
            return result
        except ClientError as clientError:
            if Wrapper.is_error_expired_token(clientError) and self.retries < self.retry:
                self.retries += 1
                self.reset_client()
                return self.delete_file(key)

            raise

    def copy_file(self, source_key, destination_key):
        # Normalize s3 path if we're on windows
        source_key = source_key.replace('\\', '/')
        destination_key = destination_key.replace('\\', '/')

        s3 = self.create_resource()
        copy_source = {
            'Bucket': self.bucket_name,
            'Key': source_key
        }

        try:
            s3.meta.client.copy(copy_source, self.bucket_name, destination_key)
        except ClientError as clientError:
            if self.retries < self.retry:
                self.retries += 1
                self.reset_client()
                return self.copy_file(source_key, destination_key)

            raise

    def move_file(self, source_key, destination_key):
        # We do a try here in case copy fails, in which case we don't try delete.
        try:
            self.copy_file(source_key, destination_key)
            self.delete_file(source_key)
        except BaseException:
            raise

# -*- coding: utf-8 -*-
import boto3

from ct_api_gateway_deployer.src.aws.aws_loader import AWSLoader


class AWSClient(AWSLoader):
    def __init__(self, file_path):
        super().__init__(file_path)

    def get_aws_client(self, service_name, **kwargs):
        """
            Parameters
            ----------
            service_name : str
               AWS's service desired to connect to.

            **kwargs: dict
                Optional args for the specific service.

            Returns
            -------
            botocore.client.ServiceName
               Returns a client for the specific service required.
        """
        return boto3.client(
            service_name,
            aws_access_key_id=self._aws_config_file['aws']['access_key_id'],
            aws_secret_access_key=self._aws_config_file['aws']['secret_access_key'],
            region_name=self._aws_config_file['region'],
            **kwargs
        )



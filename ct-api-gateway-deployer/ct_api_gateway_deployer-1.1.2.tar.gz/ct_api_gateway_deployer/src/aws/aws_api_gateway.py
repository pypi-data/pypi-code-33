# -*- coding: utf-8 -*-
from ct_api_gateway_deployer.src.common.exceptions.generic_exception import GenericException
from ct_api_gateway_deployer.src.aws.aws_client import AWSClient


class AWSApiGateway(AWSClient):
    def __init__(self, file_path):
        super().__init__(file_path)
        self._client = self.get_api_gateway_client()

    def get_api_gateway_client(self):
        """
            Returns
            -------
            botocore.client.APIGateway
               Returns a client for the AWS API Gateway.
        """
        try:
            return self.get_aws_client(service_name='apigateway')
        except Exception as e:
            print('Error to instantiate API Gateway client.')
            raise e

    def rest_api_exists(self):
        return self.get_rest_api() is not None

    def get_rest_api(self):
        if self._client is None:
            raise GenericException(message='API Gateway client is not instantiated.')

        try:
            response = self._client.get_rest_api(restApiId=self._aws_config_file['apiGateway']['rest_api_id'])
        except Exception:
            response = None

        return response

    def import_routes(self, open_api_routes_file):
        outfile = open(open_api_routes_file, "r", encoding='utf-8')
        return self._client.put_rest_api(
            restApiId=self.get_rest_api_id(),
            mode='overwrite',
            parameters={
                'ignore': 'documentation',
                'endpointConfigurationTypes': 'REGIONAL'
            },
            body=outfile.read()
        )

    def deploy(self):
        return self._client.create_deployment(
            restApiId=self.get_rest_api_id(),
            stageName=self.get_stage_name()
        )

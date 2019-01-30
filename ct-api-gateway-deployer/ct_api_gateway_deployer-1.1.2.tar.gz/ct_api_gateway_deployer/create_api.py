# -*- coding: utf-8 -*-
import os

from ct_api_gateway_deployer.src.common.exceptions.generic_exception import GenericException
from ct_api_gateway_deployer.src.aws.aws_api_gateway import AWSApiGateway
from ct_api_gateway_deployer.src.open_api_parser import OpenAPIParser
from ct_api_gateway_deployer.src.validator import Validator


def create_api():
    # Get arguments
    args = Validator.args_validator()
    output_path = args.output_openapifile_path[0]

    # Load AWS Config and initialize boto3
    api_gateway = AWSApiGateway(args.aws_config[0])

    # Read routes file and create OpenAPI file
    open_api_parser = OpenAPIParser(
        input_path=args.routes[0],
        output_path=output_path,
        api_gateway=api_gateway
    )
    open_api_parser.parse()
    open_api_parser.flush()

    # Check if instance of API Gateway exists
    if not api_gateway.rest_api_exists():
        raise GenericException(message='Cannot find API Gateway in AWS service. Check aws configuration file.')

    # Import API from the new file
    api_gateway.import_routes(open_api_routes_file=output_path)

    # Deploy
    api_gateway.deploy()
    if not args.keep_output_openapifile and os.path.isfile(output_path):
        os.remove(output_path)

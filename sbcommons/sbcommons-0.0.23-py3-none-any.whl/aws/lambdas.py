import json
from typing import Dict

import boto3


def invoke(function_name: str, event: Dict):
    lambda_resource = boto3.client('lambda')
    lambda_resource.invoke(
        FunctionName=function_name,
        InvocationType='Event',
        Payload=json.dumps(event)
    )

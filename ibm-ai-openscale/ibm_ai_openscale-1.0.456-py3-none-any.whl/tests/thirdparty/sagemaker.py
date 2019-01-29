# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from .Engine import Engine
from preparation_and_cleaning import *
import boto3
import time
import json


class BreastCancer(Engine):

    credentials = get_aws_credentials()

    def score(self, binding_details, subscription_details):
        access_id = binding_details['entity']['credentials']['access_key_id']
        access_key = binding_details['entity']['credentials']['secret_access_key']
        region = binding_details['entity']['credentials']['region']
        endpoint_name = subscription_details['entity']['deployments'][0]['name']

        runtime = boto3.client('sagemaker-runtime',
                               region_name=region,
                               aws_access_key_id=access_id,
                               aws_secret_access_key=access_key)

        fields = ['radius_mean', 'texture_mean', 'perimeter_mean', 'area_mean', 'smoothness_mean', 'compactness_mean',
                  'concavity_mean', 'concave points_mean', 'symmetry_mean', 'fractal_dimension_mean', 'radius_se',
                  'texture_se', 'perimeter_se', 'area_se', 'smoothness_se', 'compactness_se', 'concavity_se',
                  'concave points_se', 'symmetry_se', 'fractal_dimension_se', 'radius_worst', 'texture_worst',
                  'perimeter_worst', 'area_worst', 'smoothness_worst', 'compactness_worst', 'concavity_worst',
                  'concave points_worst', 'symmetry_worst', 'fractal_dimension_worst']
        payload = "17.02,23.98,112.8,899.3,0.1197,0.1496,0.2417,0.1203,0.2248,0.06382,0.6009,1.398,3.999,67.78,0.008268,0.03082,0.05042,0.01112,0.02102,0.003854,20.88,32.09,136.1,1344,0.1634,0.3559,0.5588,0.1847,0.353,0.08482\n17.02,23.98,112.8,899.3,0.1197,0.1496,0.2417,0.1203,0.2248,0.06382,0.6009,1.398,3.999,67.78,0.008268,0.03082,0.05042,0.01112,0.02102,0.003854,20.88,32.09,136.1,1344,0.1634,0.3559,0.5588,0.1847,0.353,0.08482"

        start_time = time.time()
        response = runtime.invoke_endpoint(EndpointName=endpoint_name,
                                           ContentType='text/csv',
                                           Body=payload)
        response_time = time.time() - start_time
        result = json.loads(response['Body'].read().decode())

        values = []
        for v in payload.split('\n'):
            values.append([float(s) for s in v.split(',')])

        request = {'fields': fields, 'values': values}
        response = {
            'fields': list(result['predictions'][0]),
            'values': [list(x.values()) for x in result['predictions']]
        }

        self.latest_request = request
        self.latest_response = response
        self.latest_response_time = response_time

        return request, response, response_time

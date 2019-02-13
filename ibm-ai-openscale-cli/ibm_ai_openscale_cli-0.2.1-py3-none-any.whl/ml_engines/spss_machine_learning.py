# coding=utf-8
from watson_machine_learning_client import WatsonMachineLearningAPIClient
from requests.auth import HTTPBasicAuth

import logging
import json
import time
import requests
from ibm_ai_openscale.supporting_classes import PayloadRecord
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict

logger = logging.getLogger(__name__)

class SPSSMachineLearningEngine:

    def __init__(self, credentials, deployment_details):
        self._deployment_details = deployment_details
        self._credentials = credentials

    def get_deployment_details(self):
        return self._deployment_details

    def score(self, subscription, data):
        subscription_details = subscription.get_details()
        scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']
        input_table_id = subscription_details['entity']['asset_properties']['input_data_schema']['id']

        start_time = time.time()
        response = requests.post( url=scoring_url, json=data,
                                    auth=HTTPBasicAuth( username=self._credentials['username'],
                                                        password=self._credentials['password'] ) )
        response_time = time.time() - start_time

        if 'error' in str(response.json()):
           logger.warning('WARN: Found error in scoring response: {}'.format(str(response.json)))

        result = response.json()

        record = PayloadRecord(request=data, response=result, response_time=int(response_time))
        return record
# coding=utf-8
from watson_machine_learning_client import WatsonMachineLearningAPIClient

import logging
import json
import time
import requests
from ibm_ai_openscale.supporting_classes import PayloadRecord
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict

logger = logging.getLogger(__name__)

class AzureMachineLearningEngine:

    def __init__(self, deployment_details):
        self._deployment_details = deployment_details

    def get_deployment_details(self):
        return self._deployment_details

    def score(self, subscription, data):
        subscription_details = subscription.get_details()
        scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']
        body = str.encode(json.dumps(data))

        token = subscription_details['entity']['deployments'][0]['scoring_endpoint']['credentials']['token']
        headers = subscription_details['entity']['deployments'][0]['scoring_endpoint']['request_headers']
        headers['Authorization'] = ('Bearer ' + token)

        start_time = time.time()
        response = requests.post(url=scoring_url, data=body, headers=headers)
        response_time = time.time() - start_time

        if 'error' in str(response.json()):
           logger.warning('WARN: Found error in scoring response: {}'.format(str(response.json)))

        result = response.json()

        ###
        # temporary
        # cast fields to floats and ints
        # issue: https://github.ibm.com/aiopenscale/tracker/issues/4666
        ###
        if 'Scored Probabilities' in result['Results']['output1'][0].keys():
            result['Results']['output1'][0]['Scored Probabilities'] = [float(result['Results']['output1'][0]['Scored Probabilities'])]
        numerical = ['LoanDuration', 'LoanAmount', 'InstallmentPercent', 'CurrentResidenceDuration', 'Age', 'ExistingCreditsCount', 'Dependents']
        for number_field in numerical:
            if number_field in result['Results']['output1'][0].keys():
                result['Results']['output1'][0][number_field] = int(result['Results']['output1'][0][number_field])
        ###
        # end
        ###

        request = {'fields': list(data['Inputs']['input1'][0]),
                   'values': [list(x.values()) for x in data['Inputs']['input1']]}
        response = {'fields': list(result['Results']['output1'][0]),
                    'values': [list(x.values()) for x in result['Results']['output1']]}

        record = PayloadRecord(request=request, response=response, response_time=int(response_time))
        return record
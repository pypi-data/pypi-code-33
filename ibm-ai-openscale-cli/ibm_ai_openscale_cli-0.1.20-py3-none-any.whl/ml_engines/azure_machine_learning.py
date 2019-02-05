# coding=utf-8
from watson_machine_learning_client import WatsonMachineLearningAPIClient

import logging
import json
import time
import requests
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict

logger = logging.getLogger(__name__)

class AzureMachineLearningEngine:

    def __init__(self, deployment_details):
        self._deployment_details = deployment_details

    def get_deployment_details(self):
        return self._deployment_details

    def score(self, subscription, input_data):
        subscription_details = subscription.get_details()
        scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']
        data = {
            "Inputs": {
                "input1": [ input_data ],
            },
            "GlobalParameters": {
            }
        }
        body = str.encode(json.dumps(data))

        token = subscription_details['entity']['deployments'][0]['scoring_endpoint']['credentials']['token']
        headers = subscription_details['entity']['deployments'][0]['scoring_endpoint']['request_headers']
        headers['Authorization'] = ('Bearer ' + token)

        start_time = time.time()
        response = requests.post(url=scoring_url, data=body, headers=headers)
        response_time = time.time() - start_time
        # result = response.json()
        # print('Scoring results: ' + json.dumps(result, indent=2))
        # request = {'fields': list(data['Inputs']['input1'][0]),
        #            'values': [list(x.values()) for x in data['Inputs']['input1']]}
        # response = {'fields': list(result['Results']['output1'][0]),
        #             'values': [list(x.values()) for x in result['Results']['output1']]}
        # print('request: ' + str(request))
        # print('response: ' + str(response))